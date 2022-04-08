from asyncio import tasks
import pandas as pd
import numpy as np
from dateutil.parser import parse

from sentence_transformers import SentenceTransformer

from sklearn.metrics.pairwise import cosine_similarity

from datetime import *
from dateutil.relativedelta import *

import spacy


mycsvfile = "model/questions-task.csv"


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

class SpacyModel(object):
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
        sentences = df["Questions"].to_list()
        self.tasks = df["Tasks"].to_list()

        # run: 'python -m spacy download en_core_web_md' first.
        self.nlp_model = spacy.load("en_core_web_md")
        self.sentence_tokens = self.nlp_model(sentences)


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

        token = self.nlp_model(sentence)
        similarity_values = []
        for q in self.sentence_tokens:
            score = q.similarity(similarity_values)
            similarity_values.append(score)

        max_similarity = np.max(similarity_values)

        if max_similarity < 0.5:
            return "Repeat", None

        task = self.tasks[np.argmax(similarity_values)]

        task_date = get_date(sentence)
        
        return task, task_date

