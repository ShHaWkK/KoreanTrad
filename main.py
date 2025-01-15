from flask import Flask, request, render_template, jsonify
from googletrans import Translator
from korean_romanizer.romanizer import Romanizer

app = Flask(__name__)
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    # Récupération du texte envoyé par le formulaire
    text_to_translate = request.form.get('text', '').strip()
    if not text_to_translate:
        return jsonify({'error': "Le texte à traduire est vide."}), 400

    try:
        # Traduction avec Google Translator
        translation = translator.translate(text_to_translate, src='fr', dest='ko')
        translated_text = translation.text

        # Romanisation du texte traduit
        romanized_text = romanize_korean(translated_text)

        # Construction de la réponse JSON
        response = {
            'original_text': text_to_translate,
            'translated_text': translated_text,
            'pronunciation': romanized_text,
            'source_language': translation.src,
            'target_language': 'coréen'
        }
    except Exception as e:
        response = {'error': f"Une erreur s'est produite : {str(e)}"}

    return jsonify(response)

def romanize_korean(hangul_text):
    """
    Convertit un texte coréen (hangeul) en alphabet latin (romanisation).
    """
    try:
        r = Romanizer(hangul_text)
        return r.romanize()
    except Exception as e:
        return f"Erreur lors de la romanisation : {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
