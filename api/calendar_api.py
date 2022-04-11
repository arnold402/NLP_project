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
import pandas as pd
import pytz



# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
calendar_id = 'primary' # ulrich@dsi-program.com
now = datetime.datetime.utcnow().isoformat() + 'Z'
end_DSI = '2022-05-31T23:59:0.0Z'
LANGUAGE = "en"

def load_calendar():
    """
    Load the calendar and return the events_results.
    This is basic showcase, we can pass options later
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('api/token.json'):
        creds = Credentials.from_authorized_user_file('api/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'api/client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('api/token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)
    except HttpError as error:
        print('An error occurred: %s' % error)
    
    return service


# now we should implements all the queries here each as a function
def next_event(service = load_calendar(), taskdate = now):
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
        
        if LANGUAGE == "en":
            response = "Your next meeting is " + response[0] + ". It starts at " + dt.strftime(dtparse(response[1]), format=tf)
        else:
            response = "Votre prochaine reunion est " + response[0] + ". Elle debute a " + dt.strftime(dtparse(response[1]), format=tf)           
        
    except:
        response = "You dont have meetings left today"  if LANGUAGE == "en" else "Vous n'avez plus de reunion prevu pour aujourd'hui" 
    return response

def action_time(service = load_calendar(), taskdate= now):
    return datetime.datetime.now().time().strftime('%H:%M')

def repeat_question(service = load_calendar(), taskdate = now):
    return "sorry can you please repeat your question"

def repeat_question_fr(service = load_calendar(), taskdate = now):
    return "s'il vous plait pouvez-vous repeter votre question"

def tomorrow_meeting(service = load_calendar()):
  tomorrow_start = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() + 'T00:00:0.0Z'
  tomorrow_end = (datetime.date.today() + datetime.timedelta(days=1)).isoformat() + 'T23:59:0.0Z'

  events_result = service.events().list(
      calendarId=calendar_id, timeMin=tomorrow_start, timeMax=tomorrow_end,
      maxResults=10, singleEvents=True,
      orderBy='startTime').execute()

  events = events_result.get('items', [])

  tf = '%H:%M %p'
  response = [(event['summary'], 
              event['start'].get('dateTime', event['start'].get('date')), 
              event['end'].get('dateTime', event['end'].get('date'))) for event in events]

  if LANGUAGE == "en":
    response = "Your tomorow's events are as follows: ", [(response[0][0],'at', dt.strftime(dtparse(response[0][1]), format=tf)) for item in response]
  else:
    response = "Vos reunions de demain sont les suivantes: ", [(response[0][0],'a parti de', dt.strftime(dtparse(response[0][1]), format=tf)) for item in response]
  return response

def get_all_event(service = load_calendar()) :
  """ taking all event in a panda dataframe to access it easily with its rows and column"""
  source_time_zone = pytz.timezone('Africa/Johannesburg')
  target_time_zone = pytz.timezone('America/New_York')
  dsi_start_date = datetime.datetime(2022, 1, 24,0,0,0, tzinfo=None) 
  # As we are working in different timezone, we better localize the time 
  dsi_start_date_SAST = source_time_zone.localize(dsi_start_date)
  # Get events from Google Calendar API
  now = datetime.datetime.utcnow().isoformat() + 'Z'
  events_result = service.events().list(
      calendarId=calendar_id).execute()
  events_result['items']
  import pandas as pd
  all_events = pd.DataFrame(events_result['items'])
  return all_events

def format(mydate):
  """Format the date in a nice format for the reader""" 
  time = dt.strftime(dtparse(mydate['dateTime']), format= '%B %d, %Y, %r')
  timezone = mydate['timeZone']
  if timezone == 'Africa/Johannesburg' :
    timezone = "SAST"
  if timezone == 'America/New_York' :
    timezone = "EST"    
  return(time+' '+ timezone  )

def is_on(event, topic = 'NLP'):
  try :
     return(topic in event)
  except :
    return False

def readytoread(eventdf):
  s = 'The list of concerned event are : '
  i = 0
  for row in eventdf.itertuples():
      i += 1
      s = s+ ' Event number ' + str(i) +":"
      s = s+ (row.summary + " starting at " +  row.start + " and ending at "+ row.end)
      
  s =s+ " You have " + str(i)  +" such event, Thank you for asking."
  return(s) 

def readytoread_fr(eventdf):
  s = 'Votre liste de reunions est la suivante : '
  i = 0
  for row in eventdf.itertuples():
      i += 1
      s = s+ ' Reunion numero ' + str(i) +":"
      s = s+ (row.summary + " de " +  row.start + " a "+ row.end)
      
  s =s+ " Vous avez " + str(i)  +" de ce genre d'evenements."
  return(s)   

def list_event_on(service = load_calendar(),topic= 'NLP') :
  
  all_events = get_all_event()
  
  try :  
    idx = [i for i in range(len(all_events['summary'])) if is_on(all_events['summary'][i], topic)]
    if len(idx)==0 :
      return('There is no such event' if LANGUAGE=="en" else "Vous n'avez aucun evenements de ce genre")
      
    on_topic = all_events.loc[idx, ['summary', 'start','end']]
    on_topic["start"] =  (on_topic["start"]).apply(format) 
    on_topic["end"] = (on_topic["end"]).apply(format) 
    return(readytoread(on_topic) if LANGUAGE=="en" else readytoread_fr(on_topic))
  except : repeat_question if LANGUAGE == "en" else repeat_question_fr


def is_ons(event, keywords):

  try :
     mybool =True
     for keyword in keywords :
       mybool = mybool and (keyword in event)
     return(mybool)
  except :
    return False

def list_event_ons(service = load_calendar(),keywords = ['Lecture','Bruce'], source_data = get_all_event(), features =  ['summary', 'start','end'] ) :
    try :  
      idx = [i for i in range(len(source_data['summary'])) if is_ons(source_data['summary'][i], keywords)]
      if len(idx)==0 :
        return('Nope! We are not having such event' if LANGUAGE=="en" else "Nous n'avons pas ce type d'evenements")
        
      on_topic = source_data.loc[idx,features]
      on_topic["start"] =  (on_topic["start"]).apply(format) 
      on_topic["end"] = (on_topic["end"]).apply(format) 

      return(readytoread(on_topic) if LANGUAGE=="en" else readytoread_fr(on_topic))
    except : repeat_question if LANGUAGE == "en" else repeat_question_fr

def get_week(date):
  """Return the full week (Sunday first) of the week containing the given date.

  'date' may be a datetime or date instance (the same type is returned).
  """
  one_day = datetime.timedelta(days=1)
  day_idx = (date.weekday() + 1) % 7  # turn sunday into 0, monday into 1, etc.
  sunday = date - datetime.timedelta(days=day_idx)
  date = sunday
  for n in range(7):
    yield date
    date += one_day

def give_start_end(timeframe):
  '''given a timeframe keyword, return the start and end in a list'''
  try :
    daynear = ['today', 'tomorrow', 'yesterday']
    for i in range(-1,2) : 
      if daynear[i] in timeframe :
        the_day_start = (datetime.date.today() + datetime.timedelta(days=i)).isoformat() + 'T00:00:0.0Z'
        the_day_end = (datetime.date.today() + datetime.timedelta(days=i)).isoformat() + 'T23:59:0.0Z'
        return([the_day_start,the_day_end ])
    
    weeknear = ['this','next','last']
    for i in range(-1,2) : 
      if (weeknear[i] in timeframe) and ('week' in timeframe) :
        the_day  = (datetime.date.today() + datetime.timedelta(days=i*7) )
        the_week = [d.isoformat() for d in get_week(the_day)]

        week_start_date = the_week[0] + 'T00:00:0.0Z'
        week_end_date = the_week[-1] + 'T23:59:0.0Z'
        return([week_start_date,week_end_date ])
    number_day_in_month = [31, 28, 31, 30, 31, 30, 31, 30, 31, 30, 31, 30] 
    month_near = ['this','next','last']
    currentMonth = datetime.datetime.now().month
    currentYear = datetime.datetime.now().year
    for i in range(-1,2) :
      if (month_near[i] in timeframe and 'month' in timeframe  ) :
        month = str(currentMonth +i)

        if len(month) == 1 :
          month = '0'+month # so that March will be 03 and so on

        month_start = str(currentYear) +'-'+(month) +'-01T00:00:0.0Z'
        month_end = str(currentYear) +'-'+(month)+'-' +str(number_day_in_month[currentMonth +i -1] )+ 'T23:59:0.0Z'
        return([month_start, month_end ])
  except :
    return('Can you give a valid timeframe' if LANGUAGE=="en" else "Donne une zones horraire valide")   

def now() : 
  return datetime.datetime.utcnow().isoformat() + 'Z'

def querries( service =  load_calendar(), keywords= ['Stand-up'], timeframe = [now(), end_DSI ], maxResults = 10, features =  ['summary', 'start','end'] ) :
  """" Given keywords and timeframe, return the event corresponding to this timeframe on the keywords"""
  try :
    if len(timeframe) == 1 : # that is, the timeframe is a list of string and we will define start and end
        timeframe = give_start_end(timeframe[0])
    
    events_result = service.events().list(
      calendarId=calendar_id, timeMin = timeframe[0], timeMax=timeframe[1],
      maxResults=maxResults, singleEvents=True,
      orderBy='startTime').execute()
    # changed
    if events_result['items']==[]: return 'No such event' if LANGUAGE == "en" else "Aucun evenement"
    ##

    events = pd.DataFrame(events_result['items'])
    
    return( list_event_ons(service,keywords, source_data = events, features=features ))
  except : (repeat_question if LANGUAGE == "en" else repeat_question_fr)


## Since all element in the Queries dictionary need to call on function each, we provide the following function based on the question
def next_seminar(service,now):
  return querries(keywords = ['Seminar'])
def next_stand_ups(service= load_calendar(), now = now()):
  return list_event_ons(keywords = ['Stand-up'])
def next_stand_up(service= load_calendar(), now = now()):
  return querries(keywords=  ['Stand-up'] ,maxResults=1)
def week_stand_up(service= load_calendar(), now = now()):
  return querries(keywords=  ['Stand-up'] , timeframe = ['this week'], maxResults=100)
def lecture_on_dashboard(service= load_calendar(), now = now()):
  return querries(keywords=  ['ashboard'] , timeframe = ['next week'], maxResults=100)

def seminar_this_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['this week'], maxResults=100)
def seminar_last_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['last week'], maxResults=100)  
def seminar_next_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['next week'], maxResults=100)
def lecture_this_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['this week'], maxResults=100)
def lecture_last_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['last week'], maxResults=100)
def lecture_next_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['next week'], maxResults=100)
def talk_next_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['next week'], maxResults=100)
def talk_this_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['this week'], maxResults=100)
def talk_last_week(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['last week'], maxResults=100)

def seminar_this_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['this month'], maxResults=100)
def seminar_last_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['last month'], maxResults=100)  
def seminar_next_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['eminar'] , timeframe = ['next month'], maxResults=100)
def lecture_this_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['this month'], maxResults=100)
def lecture_last_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['last month'], maxResults=100)
def lecture_next_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['ecture'] , timeframe = ['next month'], maxResults=100)
def talk_next_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['next month'], maxResults=100)
def talk_this_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['this month'], maxResults=100)
def talk_last_month(service= load_calendar(), now = now()):
  return querries(keywords=  ['Talk'] , timeframe = ['last month'], maxResults=100)

# now let have a general function query that should pick which querry we run
# Queries is a dictionary with all the relevant functions for each task in our questions-task.csv file
Queries = {}
Queries["Get next event"] = next_event
Queries["Get time"] = action_time
Queries["Repeat"]  = repeat_question
Queries["Repeat_fr"]  = repeat_question_fr
Queries['Tommorow meeting'] = tomorrow_meeting
Queries["Event on NLP"] = list_event_on
# here we can extend this dictionary with as many topic as we can
Queries["Lecture by Bruce"] = list_event_ons
Queries['next stand ups'] = next_stand_ups
Queries['next stand up'] = next_stand_up
Queries['stand-up this week'] = week_stand_up
Queries['lecture on Dashboard'] = lecture_on_dashboard

Queries['seminars this week'] = seminar_this_week
Queries['seminars last week'] = seminar_last_week
Queries['seminars next week'] = seminar_next_week
Queries['lectures this week'] = lecture_this_week
Queries['lectures last week'] = lecture_last_week
Queries['lectures next week'] = lecture_next_week
Queries['Talks last week'] = talk_last_week
Queries['Talks next week'] = talk_next_week
Queries['Talks this week'] = talk_this_week
Queries['seminars this month'] = seminar_this_month
Queries['seminars last month'] = seminar_last_month
Queries['seminars next month'] = seminar_next_month
Queries['lectures this month'] = lecture_this_month
Queries['lectures last month'] = lecture_last_month
Queries['lectures next month'] = lecture_next_month
Queries['Talks last month'] = talk_last_month
Queries['Talks next month'] = talk_next_month
Queries['Talks this month'] = talk_this_month


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