import os
import csv
import asyncio
import aiohttp

OAUTH_TOKEN = os.environ["PRIVATE_TOKEN"]
BASE_URL = "https://www.eventbriteapi.com/v3"
HEADERS = {
    "Authorization": f"Bearer {OAUTH_TOKEN}",
}


async def fetch(session, url):
    async with session.get(url, headers=HEADERS, timeout=10) as response:
        response.raise_for_status()
        return await response.json()


async def get_my_organizations(session):
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
        if not continuation:
            break

    return organizations


async def fetch_attendees_page(session, url):
    data = await fetch(session, url)
    return data.get("attendees", []), data["pagination"]["has_more_items"]


async def get_attendees_by_org(session, organization_id):
    attendees = []
    page = 1
    has_more_items = True

    while has_more_items:
        url = f"{BASE_URL}/organizations/{organization_id}/attendees/?expand=event&page={page}"
        page_attendees, has_more_items = await fetch_attendees_page(session, url)
        attendees.extend(page_attendees)
        page += 1

    return attendees


def export_attendees_to_csv(attendees, output_file='attendees.csv'):
    headers = ['organization_id', 'event_id', 'event_name', 'event_start', 'checked_in',
               'attendee_name', 'email', 'age', 'gender', 'cell_phone']

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        for attendee in attendees:
            event = attendee.get('event', {})
            profile = attendee.get('profile', {})

            row = [
                event.get('organization_id', ''),
                attendee.get('event_id', ''),
                event.get('name', {}).get('text', ''),
                event.get('start', {}).get('utc', ''),
                attendee.get('checked_in', False),
                profile.get('name', ''),
                profile.get('email', ''),
                profile.get('age', ''),
                profile.get('gender', ''),
                profile.get('cell_phone', ''),
            ]
            writer.writerow(row)


async def main():
    async with aiohttp.ClientSession() as session:
        organizations = await get_my_organizations(session)

        # Fetch all attendees concurrently for each organization
        tasks = [
            get_attendees_by_org(session, int(org["id"]))
            for org in organizations
        ]
        results = await asyncio.gather(*tasks)

        # Flatten list of lists
        all_attendees = [attendee for sublist in results for attendee in sublist]

        export_attendees_to_csv(all_attendees, "data/output.csv")

        for org, attendees in zip(organizations, results):
            print(f"{org['name']} - {len(attendees)} attendees")


if __name__ == "__main__":
    asyncio.run(main())
