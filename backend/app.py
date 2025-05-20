# app.py (Backend en Flask)
from flask import Flask, request, jsonify, make_response
from textblob import TextBlob
from textblob import download_corpora
from nltk.corpus import wordnet
import random
from flask_cors import CORS
import nltk
import os

# Asegurar ruta para nltk
nltk.data.path.append("/opt/render/nltk_data")

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Netlify

@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    text = request.json.get('text')
    if len(text) > 1000:
        return jsonify({"error": "Texto demasiado largo (máx. 1000 caracteres)"}), 400

    # Descargar los corpora necesarios directamente desde TextBlob
    download_corpora.download_all()

    try:
        blob = TextBlob(text)
        paraphrased = " ".join([
            paraphrase_sentence(str(sentence))
            for sentence in blob.sentences
        ])
        return jsonify({"result": paraphrased})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def paraphrase_sentence(sentence):
    blob = TextBlob(sentence)
    return " ".join([
        random.choice(list(set([lemma.name() for syn in wordnet.synsets(word)
                          for lemma in syn.lemmas()])))
        if wordnet.synsets(word) else word
        for word in blob.words
    ])

@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Servidor Flask activo. Usa POST /paraphrase para parafrasear texto."})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
