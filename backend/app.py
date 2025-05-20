# app.py (Backend en Flask)
from flask import Flask, request, jsonify, make_response
from textblob import TextBlob
from nltk.corpus import wordnet
import random
from flask_cors import CORS  # Para evitar errores CORS

app = Flask(__name__)
CORS(app)  # Permite peticiones desde Netlify

@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    text = request.json.get('text')
    if len(text) > 1000:  # Limita a 1000 caracteres
        return jsonify({"error": "Texto demasiado largo (máx. 1000 caracteres)"}), 400

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

if __name__ == '__main__':
    app.run()