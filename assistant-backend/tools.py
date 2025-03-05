import datetime
from langchain_core.tools import tool
from os import environ as env

import requests


cal_api_endpoint = "https://api.cal.com/v2"
cal_api_key = env.get("CAL_API_KEY")
cal_event_id = "1979939"


@tool
def get_next_available_meeting():
    """Returns the next available meeting in JSON format. All times are in UTC time."""
    current_time = datetime.datetime.now(datetime.timezone.utc)
    current_date = current_time.strftime("%Y-%m-%d")
    current_date_plus_one_week = (current_time + datetime.timedelta(days=7)).strftime(
        "%Y-%m-%d"
    )
    url = f"{cal_api_endpoint}/slots?start={current_date}&end={current_date_plus_one_week}&eventTypeId={cal_event_id}"

    print("get_next_available_meeting")

    try:
        response = requests.get(
            url,
            headers={
                "Authorization": f"Bearer {cal_api_key}",
                "cal-api-version": "2024-09-04",
            },
        )
        if response.status_code != 200:
            print("error", response.status_code, response.text)
            return f"Error getting schedules: {response.status_code} - {response.text}"
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error getting schedules: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

    try:
        slots = data["data"]
    except (KeyError, IndexError):
        return "No schedule data found."

    # It is great - I only need to return the availability data for LLM
    # Otherwise, I would need to create a logic to return the next available appointment in python
    print("slots", slots)
    return slots


@tool
def reserve_meeting(slot_start):
    """
    Reserves a meeting slot on Cal.com

    Args:
        slot_start: Start time of the slot in ISO format (e.g., "2024-09-04T09:00:00Z")

    Returns:
        Reservation confirmation or error message
    """
    url = f"{cal_api_endpoint}/bookings"

    print("reserve_meeting", slot_start)

    payload = {
        "attendee": {
            "language": "en",
            "name": "John Doe",
            "email": "john.doe@example.com",
            "timeZone": "Europe/Prague"
        },
        "start": slot_start,
        "eventTypeId": int(cal_event_id)
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={
                "Authorization": f"Bearer {cal_api_key}",
                "cal-api-version": "2024-08-13",
                "Content-Type": "application/json"
            },
        )
        if response.status_code != 200:
            print("error", response.status_code, response.text)
            return f"Error reserving meeting: {response.status_code} - {response.text}"
        data = response.json()
        print("data reserve_meeting", data)
        return data
    except requests.exceptions.RequestException as e:
        return f"Error reserving meeting: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"
