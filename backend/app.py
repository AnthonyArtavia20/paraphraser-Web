import random
import re
from flask import Flask, request, jsonify
from textblob import TextBlob, download_corpora
from nltk.corpus import wordnet
from flask_cors import CORS
import nltk
import os

# Render usa este path para nltk
nltk.data.path.append("/opt/render/nltk_data")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({"message": "Servidor Flask activo. Usa POST /paraphrase para parafrasear texto."})

@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "No se proporcionó texto"}), 400
    if len(text) > 1000:
        return jsonify({"error": "Texto demasiado largo (máx. 1000 caracteres)"}), 400

    download_corpora.download_all()

    try:
        blob = TextBlob(text)
        paraphrased_parts = [
            paraphrase_sentence(str(sentence))
            for sentence in blob.sentences
        ]
        paraphrased_text = " ".join(part["text"] for part in paraphrased_parts)
        marked_text = " ".join(part["marked"] for part in paraphrased_parts)
        return jsonify({
            "result": paraphrased_text,
            "highlighted": marked_text
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def paraphrase_sentence(sentence):
    blob = TextBlob(sentence)
    result = []
    marked = []

    for word in blob.words:
        if wordnet.synsets(word):
            synonyms = [
                lemma.name().replace("_", " ")
                for syn in wordnet.synsets(word)
                for lemma in syn.lemmas()
                if re.match("^[a-zA-ZáéíóúñÁÉÍÓÚÑ]+$", lemma.name())
            ]
            if synonyms:
                chosen = random.choice(synonyms)
                if chosen.lower() != word.lower():
                    result.append(chosen)
                    marked.append(f"<mark>{chosen}</mark>")
                    continue

        result.append(word)
        marked.append(word)

    return {
        "text": " ".join(result),
        "marked": " ".join(marked)
    }

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
