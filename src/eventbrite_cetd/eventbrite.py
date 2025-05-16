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


def get_attendees_by_event(event_id: int):
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

def get_attendees_by_org(organization_id: int):
    url = f"{BASE_URL}/organizations/{organization_id}/attendees/?expand=event"
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

import csv

def export_attendees_to_csv(attendees, output_file='attendees.csv'):
    """
    Exports a list of Eventbrite attendees to a CSV file.

    :param attendees: List of attendee dictionaries from the Eventbrite API.
    :param output_file: Filename for the CSV output.
    """
    # Define CSV headers
    headers = ['organization_id', 'event_id', 'event_name', 'event_start', 'checked_in', 'attendee_name', 'email', 'age', 'gender', 'cell_phone']

    # Open CSV file for writing
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(headers)

        # Process each attendee
        for attendee in attendees:
            organization_id = attendee.get('event', {}).get('organization_id', '')
            event_id = attendee.get('event_id', '')
            event_name = attendee.get('event', {}).get('name', {}).get('text', '')
            event_start = attendee.get('event', {}).get('start', {}).get('utc', '')  # Can be .get('local') if preferred
            checked_in = attendee.get('checked_in', False)
            name = attendee.get('profile', {}).get('name', '')
            email = attendee.get('profile', {}).get('email', '')

            # Try to get cell_phone from profile
            profile = attendee.get('profile', {})
            cell_phone = profile.get('cell_phone', '')
            age = profile.get('age', '')
            gender = profile.get('gender', '')


            # Write row to CSV
            writer.writerow([organization_id, event_id, event_name, event_start, checked_in, name, email, age, gender, cell_phone])



if __name__ == "__main__":
    organizations = get_my_organizations()
    for organization in organizations:
        print(organization["name"])
        id = int(organization["id"])
        attendees = get_attendees_by_org(id)
        for attendee in attendees:
            print(attendee["profile"])
        
        export_attendees_to_csv(attendees, "data/output.csv")
        # events = get_events(id)

        # for event in events:
        #     print(event["name"]["text"])
        #     event_id = int(event["id"])
        #     attendees = get_attendees_by_event(event_id)
        #     for attendee in attendees:
        #         print(attendee["profile"])
    # main()
