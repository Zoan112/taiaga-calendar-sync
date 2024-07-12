import datetime
import os
import requests
import json
from zoneinfo import ZoneInfo
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

def get_timezone():
    """Get the timezone from environment variable or use UTC as default."""
    return os.environ.get('TIMEZONE', 'UTC')

def get_day_boundaries(timezone):
    """Get the start and end of the current day in the specified timezone."""
    tz = ZoneInfo(timezone)
    now = datetime.datetime.now(tz)
    start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = start_of_day + datetime.timedelta(days=1, microseconds=-1)
    return start_of_day, end_of_day

def get_events(timezone):
    """Fetches events from Google Calendar for the current day in the specified timezone."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    
    try:
        service = build("calendar", "v3", credentials=creds)
        start_of_day, end_of_day = get_day_boundaries(timezone)
        
        print(f"Fetching events for {start_of_day.date()} in {timezone}")
        events_result = service.events().list(
            calendarId="primary",
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy="startTime"
        ).execute()
        
        events = events_result.get("items", [])
        if not events:
            print("No events found for today.")
            return []
        return events
    except HttpError as error:
        print(f"An error occurred while fetching events: {error}")
        return []

def get_taiga_auth_token():
    """Authenticates with Taiga and returns the auth token."""
    taiga_username = os.environ.get('TAIGA_USERNAME')
    taiga_password = os.environ.get('TAIGA_PASSWORD')
    print(f"{taiga_username} {taiga_password}")
    if not taiga_username or not taiga_password:
        raise ValueError("Taiga credentials not set in environment variables.")
    
    url = "https://api.taiga.io/api/v1/auth"
    payload = json.dumps({
        "type": "normal",
        "username": taiga_username,
        "password": taiga_password
    })
    headers = {'Content-Type': 'application/json'}
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        data = response.json()
        return data['auth_token']
    except requests.RequestException as e:
        print(f"Error authenticating with Taiga: {e}")
        return None

def sync_event_to_taiga(event, taiga_auth_token, timezone):
    """Creates a Taiga task for a given Google Calendar event."""
    project_id = os.environ.get('TAIGA_PROJECT_ID')
    user_story_id = os.environ.get('TAIGA_USER_STORY_ID')
    
    if not project_id or not user_story_id:
        raise ValueError("Taiga project or user story ID not set in environment variables.")
    
    url = "https://api.taiga.io/api/v1/tasks"
    start_time = event['start'].get('dateTime', event['start'].get('date'))
    
    # Convert start time to specified timezone
    if isinstance(start_time, str):
        start_time = datetime.datetime.fromisoformat(start_time.replace('Z', '+00:00'))
    start_time = start_time.astimezone(ZoneInfo(timezone))
    
    payload = json.dumps({
        "project": project_id,
        "user_story": user_story_id,
        "subject": f"{event['summary']} - {start_time.strftime('%Y-%m-%d %H:%M %Z')}"
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {taiga_auth_token}'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error creating Taiga task for event '{event['summary']}': {e}")
        return None

def main():
    timezone = get_timezone()
    events = get_events(timezone)
    if not events:
        return
    
    taiga_auth_token = get_taiga_auth_token()
    if not taiga_auth_token:
        print("Failed to authenticate with Taiga. Exiting.")
        return
    
    for event in events:
        taiga_task = sync_event_to_taiga(event, taiga_auth_token, timezone)
        if taiga_task:
            print(f"Created Taiga task: {taiga_task['subject']}")

if __name__ == "__main__":
    main()