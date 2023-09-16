from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calender():
    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Get the current date in the correct timezone (adjust timezone as needed)
    current_datetime = datetime.now()
    # print(current_datetime)

    # Initialize a dictionary to store time intervals and locations
    time_location_dict = {i: None for i in range(24)}

    # Fetch all calendars
    # print("Fetching all calendars:")
    calendar_list = service.calendarList().list().execute().get('items', [])

    time_min = current_datetime.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=4)

    time_min = time_min.isoformat() + 'Z'

    # Set timeMax to the end of the current day
    time_max = current_datetime.replace(hour=23, minute=59, second=59, microsecond=999999) + timedelta(hours=4)

    time_max = time_max.isoformat() + 'Z'

    calendar = calendar_list[0]
    # print(calendar['id'])
    # print(f"Calendar: {calendar['summary']}")
    events_result = service.events().list(
        calendarId=calendar['id'],
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        print(f'No events found for today in {calendar["summary"]}.')
    else:
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            location = event.get('location', 'Location not specified')  # Get event location or use a default value
            
            start_time = datetime.fromisoformat(start)
            end_time = datetime.fromisoformat(end)
            
            for interval_index in range(start_time.hour, end_time.hour):
                time_location_dict[interval_index] = location

    return time_location_dict

