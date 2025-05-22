"""This script fetches attendee data from the Eventbrite API for all organizations associated with the authenticated user and exports it to a CSV file.

It handles pagination for both organizations and attendees to ensure all data is retrieved.
The script uses asynchronous HTTP requests for efficient data fetching.
"""

import asyncio
import csv
import logging
import os

import aiohttp

OAUTH_TOKEN = os.environ["PRIVATE_TOKEN"]
BASE_URL = "https://www.eventbriteapi.com/v3"
HEADERS = {
    "Authorization": f"Bearer {OAUTH_TOKEN}",
}


async def fetch(session: aiohttp.ClientSession, url: str) -> dict:
    """Fetches data from a given URL using an aiohttp session.

    Args:
        session: An aiohttp client session.
        url: The URL to fetch data from.

    Returns:
        A dictionary containing the JSON response from the URL.

    Raises:
        aiohttp.ClientResponseError: If the HTTP request returns an unsuccessful status code.
    """
    async with session.get(url, headers=HEADERS, timeout=10) as response:
        response.raise_for_status()
        return await response.json()


async def get_my_organizations(session: aiohttp.ClientSession) -> list[dict]:
    """Retrieves all organizations associated with the authenticated user.

    This function handles pagination to ensure all organizations are fetched.

    Args:
        session: An aiohttp client session.

    Returns:
        A list of dictionaries, where each dictionary represents an organization.
    """
    url = f"{BASE_URL}/users/me/organizations/"
    organizations = []
    continuation = None

    while True:
        paginated_url = url
        if continuation:
            paginated_url += f"?continuation={continuation}"

        data = await fetch(session, paginated_url)
        organizations.extend(data["organizations"])

        continuation = data["pagination"].get("continuation")
        has_more_items = data["pagination"].get("has_more_items")
        if not has_more_items:
            break

    return organizations


async def fetch_attendees_page(session: aiohttp.ClientSession, url: str) -> tuple[list[dict], str | None, bool]:
    """Fetches a single page of attendees from a given URL.

    Args:
        session: An aiohttp client session.
        url: The URL to fetch attendees from.

    Returns:
        A tuple containing:
            - A list of dictionaries, where each dictionary represents an attendee.
            - The continuation token for the next page, or None if no more pages.
            - A boolean indicating if there are more items.
    """
    data = await fetch(session, url)
    return data.get("attendees", []), data["pagination"].get("continuation"), data["pagination"].get("has_more_items")


async def get_attendees_by_org(session: aiohttp.ClientSession, organization_id: int) -> list[dict]:
    """Retrieves all attendees for a specific organization.

    This function handles pagination and expands event details for each attendee.

    Args:
        session: An aiohttp client session.
        organization_id: The ID of the organization to retrieve attendees for.

    Returns:
        A list of dictionaries, where each dictionary represents an attendee.
    """
    attendees = []
    continuation = None

    while True:
        url = f"{BASE_URL}/organizations/{organization_id}/attendees/?expand=event"
        if continuation:
            url += f"&continuation={continuation}"

        page_attendees, continuation, has_more_items = await fetch_attendees_page(session, url)
        attendees.extend(page_attendees)

        if not has_more_items:
            break

    return attendees


def export_attendees_to_csv(attendees: list[dict], output_file: str) -> None:
    """Exports a list of attendee data to a CSV file.

    Args:
        attendees: A list of dictionaries, where each dictionary represents an attendee
                   (as returned by Eventbrite API, including 'event' and 'profile' nested data).
        output_file: The name of the CSV file to write the data to. Defaults to "attendees.csv".
    """
    headers = ["organization_id", "event_id", "event_name", "event_start", "checked_in",
               "attendee_name", "email", "age", "gender", "cell_phone"]

    with open(output_file, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for attendee in attendees:
            event = attendee.get("event", {})
            profile = attendee.get("profile", {})

            row = [
                event.get("organization_id", ""),
                attendee.get("event_id", ""),
                event.get("name", {}).get("text", ""),
                event.get("start", {}).get("utc", ""),
                attendee.get("checked_in", False),
                profile.get("name", ""),
                profile.get("email", ""),
                profile.get("age", ""),
                profile.get("gender", ""),
                profile.get("cell_phone", ""),
            ]
            writer.writerow(row)


async def main(logger: logging.Logger, output_file: str = "data/attendees.csv") -> None:
    """Main function to orchestrate fetching and exporting Eventbrite attendee data.

    This function performs the following steps:
    1. Fetches all organizations for the authenticated user.
    2. Concurrently fetches all attendees for each organization.
    3. Flattens the list of attendees.
    4. Exports all attendees to a CSV file named "data/output.csv".
    5. Prints a summary of attendees per organization.

    Args:
        logger: A logging.Logger instance for logging messages.
        output_file: The path to the output CSV file. Defaults to "data/attendees.csv".
    """
    try:
        async with aiohttp.ClientSession() as session:
            organizations = await get_my_organizations(session)
            logger.info(f"Found {len(organizations)} organizations.")

            # Fetch all attendees concurrently for each organization
            tasks = [
                get_attendees_by_org(session, int(org["id"]))
                for org in organizations
            ]
            results = await asyncio.gather(*tasks)

            # Flatten list of lists
            all_attendees = [attendee for sublist in results for attendee in sublist]
            logger.info(f"Total attendees fetched: {len(all_attendees)}")

            # Ensure the 'data' directory exists
            os.makedirs("data", exist_ok=True)
            export_attendees_to_csv(all_attendees, output_file)
            logger.info(f"Attendee data exported to {output_file}")

            for org, attendees in zip(organizations, results):
                logger.info(f"{org['name']} - {len(attendees)} attendees")
    except Exception:
        logger.exception("An error occurred in main:")
        raise # Re-raise the exception after logging


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    app_logger = logging.getLogger(__name__)

    asyncio.run(main(app_logger))
