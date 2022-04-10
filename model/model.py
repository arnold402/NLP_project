from asyncio import tasks
import pandas as pd
import numpy as np
from dateutil.parser import parse

from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity

import fasttext

from datetime import *; from dateutil.relativedelta import *

mycsvfile = "model/questions-task.csv"

PRETRAINED_MODEL_PATH = 'model/lid.176.bin'


def get_period(string):
    """Checks if sentence contains any period of the day
    """
    if "morning" in string.lower():
        return "morning" 
    elif "afternoon" in string.lower():
        return "afternoon" 
    elif "evening" in string.lower():
        return "evening"
    else:
        return None

def get_date(string, fuzzy=False):
    """
    Returns the data in a string can be interpreted as a date.
    Args:
       string (str) 
           -string to check for date
       fuzzy: bool 
           -ignore unknown tokens in string if True
    Returns:
        Date if any
    """
    try: 
        mydate = parse(string, fuzzy=fuzzy)
        return mydate
    except ValueError:
        TODAY = date.today()
        period = get_period(string)

        if "today" in string.lower():
            return TODAY, period
        elif "tomorrow" in string.lower():
            return TODAY + relativedelta(days=+1), period
        elif "this week" in string.lower():
            return "this week"
        elif "next week" in string.lower():
            return "next week"
        else:
            return None 

class DistanceModel(object):
    """Implementation of simple model for computing the similarity between
       sentences using the cosine similarity between the embedded vectors
    """

    def __init__(self, mycsvfile=mycsvfile):
        """
        Initialise the model for sentence encording using the sentenceTransform library
        and apply the encording to all the sentences in our database
        Args:
            ---
        """

        df = pd.read_csv(mycsvfile)
        sentences_en = df["Questions_en"].to_list()
        sentences_fr = df["Questions_fr"].to_list()
        self.tasks = df["Tasks"].to_list()

        self.model = SentenceTransformer('distiluse-base-multilingual-cased-v1')
        self.sentence_embeddings_en = self.model.encode(sentences_en)
        self.sentence_embeddings_fr = self.model.encode(sentences_fr)

        self.lang_detector = fasttext.load_model(PRETRAINED_MODEL_PATH)


    def predict(self, sentence):
        """
        Return the sentence predicted by the picking the sentence from out database
        with the highest cosine similarity with the input sentence
        Args:
            sentence (sting)
              -input sentence
        Returns
            task (string)
              -Action to be perfomed by the API
            date (datatime.date)
              - a date time, a string or none if it can't read it
        """

        one_embedding = self.model.encode(sentence)
        distances_en = cosine_similarity([one_embedding], self.sentence_embeddings_en)
        distances_fr = cosine_similarity([one_embedding], self.sentence_embeddings_fr)
        distances = (distances_en + distances_fr)/2

        max_dist = np.max(distances)

        lang = self.lang(sentence)

        thresh_hold = 0.5 #if lang == "en" else 0.2

        if max_dist < thresh_hold:
            if lang == "en":
                return "Repeat", None
            else:
                return "Repeat_fr", None

        task = self.tasks[np.argmax(distances)]

        task_date = get_date(sentence)
        
        return task, task_date
    
    def lang(self, sentence):
        """
        Use a pretrained model to detect the language, for now we only want french and english but this could literally be any language
        Args:
            sentence (string)
        Returns:
            language code (string)
             - en for english or fr for french
        """
        
        lr, _ = self.lang_detector.predict(sentence)
        
        return "en" if "en" in lr[0] else "fr"


