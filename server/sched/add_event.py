from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import os.path
import pickle

SCOPES = ['https://www.googleapis.com/auth/calendar']


def add_event(start_index, end_index, task, location, description):

    creds = None

    if os.path.exists('./data/token.pickle'):
        with open('./data/token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('./data/token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    current_date = datetime.now().date()

    start_time = datetime(current_date.year, current_date.month, current_date.day, start_index, 0, 0).isoformat()
    next_day = 0
    if end_index >=24:
        end_index -= 24
        next_day = 1
    end_time = datetime(current_date.year, current_date.month, current_date.day + next_day, end_index, 0, 0).isoformat()

    event = {
        'summary': task,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': "America/Detroit",
        },
        'end': {
            'dateTime': end_time,
            'timeZone': "America/Detroit",
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 20},
            {'method': 'popup', 'minutes': 10},
            ],
        },
        }
    
    calendar_list = service.calendarList().list().execute().get('items', [])
    # print(calendar_list[2])
    event = service.events().insert(calendarId=calendar_list[2]['id'], body=event).execute()
