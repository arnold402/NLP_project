
# DSI Virtual Assistant 

Simple chatbot that interacts with google calendar 

## How to run this app

First, clone this repository and open a terminal inside the root folder.

Create and activate a new virtual environment (recommended) by running
the following:

```bash
python3 -m venv myvenv
source myvenv/bin/activate
```

Install the requirements:

```bash
pip install -r requirements.txt
```

Download pretrained model for encoding

```bash
wget -O model/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

Run the app:

```bash
python Bot.py
```


