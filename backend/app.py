from flask import Flask, request, jsonify
from textblob import TextBlob
from textblob import download_corpora
from flask_cors import CORS
import nltk
import os

# Forzar ruta donde nltk/textblob descarga los datos en Render
nltk.data.path.append("/opt/render/nltk_data")

# Inicializar Flask
app = Flask(__name__)
CORS(app)

# Ruta principal (opcional)
@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Servidor Flask activo. Usa POST /paraphrase para parafrasear texto."})

# Ruta de parafraseo
@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    text = request.json.get('text')
    if not text:
        return jsonify({"error": "No se proporcionó texto"}), 400
    if len(text) > 1000:
        return jsonify({"error": "Texto demasiado largo (máx. 1000 caracteres)"}), 400

    # Descargar datos requeridos por TextBlob
    download_corpora.download_all()

    try:
        blob = TextBlob(text)
        # Parafrasear cada oración con traducción ida y vuelta (ES → FR → ES)
        paraphrased = " ".join([
            paraphrase_sentence(str(sentence))
            for sentence in blob.sentences
        ])
        return jsonify({"result": paraphrased})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Función de parafraseo con traducción
def paraphrase_sentence(sentence):
    try:
        blob = TextBlob(sentence)
        return str(blob.translate(to="fr").translate(to="es"))
    except Exception:
        return sentence  # Si falla, devuelve la oración original

# Configuración del puerto (para Render)
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
