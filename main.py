#!/usr/bin/env python
# coding: utf-8

# In[8]:


from __future__ import print_function

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# scope = how much you can edit the users cal. with scope = auth/calendar, editing and viewing permissions 
SCOPES = ['https://www.googleapis.com/auth/calendar']


creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())


service = build('calendar', 'v3', credentials=creds)


##add event to the gcal 
def add_event(start_time,end_time,cal = "primary",name = "",description = "",location = "",timezone = "America/Detroit"):
    event = {
        'summary': name,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': timezone,
        },
        'end': {
            'dateTime': end_time,
            'timeZone': timezone,
        },
        'reminders': {
            'useDefault': False,
            'overrides': [
            {'method': 'email', 'minutes': 20},
            {'method': 'popup', 'minutes': 10},
            ],
        },
        }
    
    try:
        event = service.events().insert(calendarId=cal, body=event).execute()

    except HttpError as error:
        print('An error occurred: %s' % error)

    return True



# In[ ]:


##need to figure out which user you add to 
##https://developers.google.com/identity/protocols/oauth2/javascript-implicit-flow

##user_info 
##gets the calendars of a speicifc user and maps all their read-only names to calendar ids to 

##add_event 
##-> params: user, name, datetime, location, description, which calendar to add to (default to primary)
##if the event exists already do not add it 


##!! another function – if the taks already exists, update the descriciption 
##!! suggest actiivties – during free time, during meals; suggest stuff to do near locations based on size of break 

