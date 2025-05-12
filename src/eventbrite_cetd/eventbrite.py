import os

import requests

# Replace with your personal OAuth token
OAUTH_TOKEN = os.environ["PRIVATE_TOKEN"]
BASE_URL = "https://www.eventbriteapi.com/v3"

headers = {
    "Authorization": f"Bearer {OAUTH_TOKEN}",
}


def get_my_organizations():
    url = f"{BASE_URL}/users/me/organizations/"
    organizations = []
    has_more_items = True

    while has_more_items:
        response = requests.get(url=url, headers=headers, timeout=10)
        data = response.json()

        organizations.extend(data["organizations"])
        has_more_items = data["pagination"]["has_more_items"]

    return organizations


def get_events(organization_id: int):
    url = f"{BASE_URL}/organizations/{organization_id}/events/"
    events = []
    has_more_items = True

    while has_more_items:
        response = requests.get(url, headers=headers, timeout=10)

        data = response.json()
        events.extend(data.get("events", []))

        has_more_items = data["pagination"]["has_more_items"]

    return events


def get_attendees(event_id):
    url = f"{BASE_URL}/events/{event_id}/attendees/"
    attendees = []
    has_more_items = True

    while has_more_items:
        response = requests.get(
            url,
            headers=headers,
        )
        response.raise_for_status()
        data = response.json()
        attendees.extend(data.get("attendees", []))

        has_more_items = data["pagination"]["has_more_items"]

    return attendees


def main():
    events = get_my_events()

    for event in events:
        print(f"\nEvent: {event['name']['text']} (ID: {event['id']})")
        attendees = get_attendees(event["id"])

        if not attendees:
            print("  No attendees found.")
        else:
            for attendee in attendees:
                profile = attendee.get("profile", {})
                name = profile.get("name", "N/A")
                email = profile.get("email", "N/A")
                print(f"  Attendee: {name}, Email: {email}")


if __name__ == "__main__":
    organizations = get_my_organizations()
    for organization in organizations:
        print(organization["name"])
        id = int(organization["id"])
        events = get_events(id)

        for event in events:
            print(event["name"]["text"])
            event_id = int(event["id"])
            attendees = get_attendees(event_id)
            for attendee in attendees:
                print(attendee["profile"])
    main()
