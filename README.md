
# DSI Virtual Assistant 

Simple chatbot that interacts with google calendar. The code consist of 3 main parts.
A chatbot section, and nlp section and google calendar query api section.

The chatbot setion using google speech recogniton to listen the to users input and also to speak to the user (by converting text to speech).
The chatbot currently supports English and French. The chatbot which is called Alina, can be awaken using any of the following phrases
"Hi Alina", "Hey Alina" or "Bonjour Alina" (for french). Based on the wake up phrase, we choose the chatbot sets the default language it espects to
either English or French. The chatbot can ended be using any phrase that involves "bye" or "aurevoir".

The chatbot listens to any user and converts the any input phrase to a text (string). The spoken text is then passed to the machine learning model
which tries to identify exactly what is the user's query. For this purpose we a mulitingual model pretrained of 15 languages to encode the input sentence from user. This sentence is then compared against the english and french encording of various sentences we have our database. Each of these sentences represents a query that the assistant can beform. We use a cosine distance as a similirity metric between the new sentence endording and all the sentences in our database.
The query for the sentence with the maximum distance is selected. We also set a threshold only to valided the query of the maximum distance is aleast 0.5 (as the
cosine similarity ranges from 0 to 1). 

Finally, selected query implemented by the user is implemented using functionalities from google calendar api. This requires the user to provide a credentials file to allow the app to ascess his/her google calendar. Furthmore a little bit of string manipulations and regular expressions (handle by the date) is required to capture dates and time informations from the input sentence. The queried information from the google calendar is then passed to the text to speech functionality of the chatbot for it to respond to the user.

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


