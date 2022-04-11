
# DSI Virtual Assistant 

Simple chatbot that interacts with google calendar. The code consists of 3 main parts: a chatbot section, an nlp section and a google calendar query API section.

The chatbot setion using google speech recogniton to listen the to users input and also to speak to the user (by converting text to speech). The chatbot currently supports English and French. The chatbot, which is called Alina, can be awakened using any of the following phrases "Hi Alina", "Hey Alina" or "Bonjour Alina" (for french). Based on the wake-up phrase, we choose the chatbot sets the default language it expects to be either English or French. The chatbot can ended be using any phrase that involves "bye" or "Au Revoir".

The chatbot listens to any user and converts any input phrase to a text (string). The spoken text is then passed to the machine learning model, which tries to identify what is the user's query. For this purpose, we used a multilingual model pre-trained on 15 languages to encode the input sentence from the user. This sentence is then compared against our database's English and French encodings of various sentences. Each of these sentences represents a query that the assistant can perform. We use a cosine distance as a similarity metric between the new sentence encoding and all the sentences in our database. The query for the sentence with the maximum distance is selected. We also set a threshold only to validate the query if the maximum distance is at aleast 0.5 (as the cosine similarity ranges from 0 to 1).

Finally, the selected query is implemented using functionalities from google calendar API. The API requires the user to provide a credentials file to allow the app to access their google calendar. Furthermore, a little bit of string manipulations and regular expressions (handle by the dateutil package) is required to capture dates and time information from the input sentence. The queried information from the google calendar is then passed to the text-to-speech functionality of the chatbot to respond to the user.

## How to run this app

Create and activate a new virtual environment (recommended) by running
the following:

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

Clone this repository and open a terminal inside the root folder:
```bash
git clone https://github.com/arnold402/NLP_project.git
```
```bash
cd NLP_project
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Download pretrained model for encoding:

```bash
wget -O model/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

Run the app:

```bash
python Bot.py
```


