from flask import Flask, request, render_template, jsonify
from googletrans import Translator
import requests

app = Flask(__name__)
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/translate', methods=['POST'])
def translate():
    text_to_translate = request.form['text']
    try:
        # Traduire le texte en coréen
        translation = translator.translate(text_to_translate, src='fr', dest='ko')

        # Analyser la grammaire avec une API externe (exemple : LanguageTool)
        grammar_analysis = analyze_grammar(translation.text)

        # Construire une réponse avec explications
        response = {
            'original_text': text_to_translate,
            'translated_text': translation.text,
            'pronunciation': translation.pronunciation,
            'source_language': translation.src,
            'target_language': 'coréen',
            'grammar_analysis': grammar_analysis
        }
    except Exception as e:
        response = {
            'error': str(e)
        }

    return jsonify(response)

def analyze_grammar(text):
    api_url = "https://api.languagetool.org/v2/check"
    params = {
        'text': text,
        'language': 'ko'
    }
    try:
        response = requests.post(api_url, data=params)
        if response.status_code == 200:
            matches = response.json().get('matches', [])
            explanations = [
                {
                    'message': match['message'],
                    'suggestions': [suggestion['value'] for suggestion in match.get('replacements', [])],
                    'context': match['context']['text'],
                    'offset': match['context']['offset'],
                    'length': match['context']['length']
                } for match in matches
            ]
            return explanations
        else:
            return f"Erreur lors de l'analyse grammaticale : {response.status_code}"
    except Exception as e:
        return f"Erreur de connexion à l'API LanguageTool : {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)