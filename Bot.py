import numpy as np
import speech_recognition as sr
from gtts import gTTS
import os
import transformers

import datetime, re
import googleapiclient.discovery
import google.auth

from dateutil.parser import parse as dtparse
from datetime import datetime as dt

# Preparation for Google API
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
calendar_id = 'arnold@dsi-program.com'
gapi_creds = google.auth.load_credentials_from_file('credentials.json', SCOPES)[0]
service = googleapiclient.discovery.build('calendar', 'v3', credentials=gapi_creds)
 

# Build the assistant
class ChatBot():
    def __init__(self, name):
        print("--- starting up", name, "---")
        self.name = name

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as mic:
            print("listening...")
            audio = recognizer.listen(mic)
        try:
            self.text = recognizer.recognize_google(audio)
            print("me --> ", self.text)
        except:
            print("me -->  ERROR")

    @staticmethod
    def text_to_speech(text):
        print("assistant --> ", text)
        speaker = gTTS(text=text, lang="en", slow=False)
        speaker.save("res.mp3")
        os.system("start res.mp3")  #mac->afplay | windows->start
        os.remove("res.mp3")

    def wake_up(self, text):
        return True if self.name in text.lower() else False

    @staticmethod
    def action_time():
        return datetime.datetime.now().time().strftime('%H:%M')

    @staticmethod
    def next_event():
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


# Run the assistant
if __name__ == "__main__":
    
    assistant = ChatBot(name="alina")
    nlp = transformers.pipeline("conversational", model="microsoft/DialoGPT-medium")
    os.environ["TOKENIZERS_PARALLELISM"] = "true"

    while True:
        assistant.speech_to_text()

        ## wake up
        if assistant.wake_up(assistant.text) is True:
            res = "Hello I am Alina the assistant, what can I do for you?"
        
        ## action timet
        elif "time" in assistant.text:
            res = assistant.action_time()
        
        ## respond politely
        elif any(i in assistant.text for i in ["thank","thanks"]):
            res = np.random.choice(["you're welcome!","anytime!","no problem!","cool!","I'm here if you need me!","peace out!"])
        
        ##Events
        ## Next meeting.
        elif "next" in assistant.text:
            res = assistant.next_event()

        ## conversation
        else:   
            chat = nlp(transformers.Conversation(assistant.text), pad_token_id=50256)
            res = str(chat)
            res = res[res.find("bot >> ")+6:].strip()

        assistant.text_to_speech(res)