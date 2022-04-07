import numpy as np
import speech_recognition as sr
from gtts import gTTS
import os
import platform

import api.calendar_api as calendar_api 
from model.model import DistanceModel

# check platform 
if "Linux" in platform.system():
    player = "vlc --play-and-exit" # this is only for my local computer
elif "Darwin" in platform.system():
    player = "afplay"
elif "Windows" in platform.system():
    player = "start"
else:
    player = "start"  # not sure how to handle this. I assume we must definitely have one of these

# load the service
service = calendar_api.load_calendar()
 
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
        os.system(f"{player} res.mp3")  #mac->afplay | windows->start
        os.remove("res.mp3")

    def wake_up(self, text):
        wakeup_hey = "hey %s"%self.name
        wakeup_hi = "hi %s"%self.name 

        if wakeup_hey in text.lower() or wakeup_hi in text.lower():
            return True
        else:
            return False
    
    def good_bye(self, text):
        bye_txt = "bye %s"%self.name
        
        if bye_txt in text.lower():
            return True
        else:
            return False

# Run the assistant
if __name__ == "__main__":
    
    assistant = ChatBot(name="alina")
    nlp = DistanceModel()
    
    os.environ["TOKENIZERS_PARALLELISM"] = "true"

    while True:
        assistant.speech_to_text()

        ## wake up
        if assistant.wake_up(assistant.text) is True:
            res = "Hello I am Alina the assistant, what can I do for you?"
        
        ## respond politely
        elif any(i in assistant.text for i in ["thank","thanks"]):
            res = np.random.choice(["you're welcome!","anytime!","no problem!","cool!","I'm here if you need me!","peace out!"])
        
        ## goodbye
        elif assistant.good_bye(assistant.text) is True:
            assistant.text_to_speech("Good bye")
            break 

        ## conversation
        else:   
            query = nlp.predict(assistant.text)
            res = calendar_api.run_query(service, query) 

        assistant.text_to_speech(res)