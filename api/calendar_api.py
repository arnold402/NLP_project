from __future__ import print_function
from calendar import calendar

import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dateutil.parser import parse as dtparse
from datetime import datetime as dt

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
calendar_id = 'primary' # ulrich@dsi-program.com

def load_calendar():
    """
    Load the calendar and return the events_results.
    This is basic showcase, we can pass options later
    """
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
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
    except HttpError as error:
        print('An error occurred: %s' % error)
    
    return service

# now we should implements all the queries here each as a function
def next_event(service, taskdate):
    # we might not need the taskdate for every function
    try:
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = service.events().list(
            calendarId=calendar_id, timeMin=now,
            maxResults=1, singleEvents=True,
            orderBy='startTime').execute()

        events = events_result.get('items', [])
        #tmfmt = '%d %B, %H:%M %p'
        tf = '%H:%M %p'
        response = [(event['summary'], 
                    event['start'].get('dateTime', event['start'].get('date')), 
                    event['end'].get('dateTime', event['end'].get('date'))) for event in events][0]
        response = "Your next meeting is " + response[0] + ". It starts at " + dt.strftime(dtparse(response[1]), format=tf)            
        return response
    except:
        response = "You dont have meetings left today"   

# now let have a general function query that should pick which querry we run
# Queries is a dictionary with all the relevant functions for each task in our questions-task.csv file
Queries = {}
Queries["Get next event"] = next_event 


def run_query(service, query):
    """
    finds the relevant query to run and calls the right query function for it,
    then returns the text to be displayed by the chatbot

    Args:
        service (google calendar we have intialised)
        query (tuple)
            (sentence and date for the task (note that this maybe empty))
    """

    task, taskdate = query
    res = Queries[task](service, taskdate)

    return res

