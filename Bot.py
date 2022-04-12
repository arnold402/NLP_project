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
    def __init__(self, name, lang="en-US"):
        print("--- starting up", name, "---")
        self.name = name
        self.lang = lang

    def speech_to_text(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as mic:
            print("listening...")
            audio = recognizer.listen(mic)
        try:
            self.text = recognizer.recognize_google(audio, language=self.lang)
            print("me --> ", self.text)
        except:
            print("me -->  ERROR")
    
    def set_lang(self, lang):
        self.lang = lang

    @staticmethod
    def text_to_speech(text, lang="en"):
        print("assistant --> ", text)
        speaker = gTTS(text=text, lang=lang, slow=False)
        speaker.save("res.mp3")
        os.system(f"{player} res.mp3")  #mac->afplay | windows->start
        os.remove("res.mp3")

    def wake_up(self, text):
        wakeup_hey = "hello" #%self.name
        # wakeup_hi = "hello %s"%self.name
        wakeup_bj = "bonjour" #%self.name 

        if wakeup_hey in text.split(" ")[0].lower() or wakeup_bj in text.split(" ")[0].lower():
            return True
        else:
            return False
    
    def good_bye(self, text):
        bye_txt = "bye"
        
        if bye_txt in text.lower():
            return True
        else:
            return False
    
    def aurevoir(self, text):
        bye_txt = "au revoir"

        if bye_txt in text.lower():
            return True
        else:
            return False

# Run the assistant
if __name__ == "__main__":
    
    assistant = ChatBot(name="alina")
    nlp = DistanceModel()
    
    os.environ["TOKENIZERS_PARALLELISM"] = "true"
    
    init_languague = True
    
    while True:
        assistant.speech_to_text()

        ## wake up
        if assistant.wake_up(assistant.text) is True:
            if nlp.lang(assistant.text.split(" ")[0]) == "en":
                res = "Hello I am Alina the assistant, what can I do for you?"
                if init_languague: 
                    assistant.set_lang("en-US")
                    calendar_api.LANGUAGE = "en"
                    init_languague = False
            else:
                res = "Bonjour, je suis Alina l'assistante, que puis-je faire pour vous?"
                if init_languague:
                    assistant.set_lang("fr-FR")
                    calendar_api.LANGUAGE = "fr"
                    init_languague = False

        ## respond politely
        elif any(i in assistant.text.lower() for i in ["thank","thanks"]):
            res = np.random.choice(["you're welcome!","anytime!","no problem!","cool!","I'm here if you need me!","peace out!"])
        elif any (i in assistant.text.lower() for i in ["merci"]):
            res = np.random.choice(["je t'en prie", "de rien"])
        
        ## goodbye
        elif assistant.good_bye(assistant.text) is True:
            assistant.text_to_speech("Good bye")
            break

        ##aurevoir
        elif assistant.aurevoir(assistant.text) is True:
            assistant.text_to_speech("Aurevoir")
            break
        ## conversation
        else:   
            query = nlp.predict(assistant.text)
            res = calendar_api.run_query(service, query) 

        # lang = nlp.lang(res)
        assistant.text_to_speech(res)
            