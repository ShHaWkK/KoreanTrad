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
    # Récupération du texte envoyé par le formulaire
    text_to_translate = request.form.get('text', '').strip()
    if not text_to_translate:
        return jsonify({'error': "Le texte à traduire est vide."}), 400

    try:
        # Traduction avec Google Translator
        translation = translator.translate(text_to_translate, src='fr', dest='ko')

        # Extraction des informations
        translated_text = translation.text
        pronunciation = translation.pronunciation or generate_phonetic(translated_text)

        # Analyse grammaticale (optionnelle)
        grammar_analysis = analyze_grammar(translated_text)

        # Construction de la réponse JSON
        response = {
            'original_text': text_to_translate,
            'translated_text': translated_text,
            'pronunciation': pronunciation,
            'source_language': translation.src,
            'target_language': 'coréen',
            'grammar_analysis': grammar_analysis
        }
    except Exception as e:
        response = {'error': f"Une erreur s'est produite : {str(e)}"}

    return jsonify(response)

def generate_phonetic(hangul_text):
    """
    Génère une transcription phonétique approximative du texte hangeul.
    """
    # mapping des caractères hangeul aux sons latins
    phonetic_map = {
        'ㄱ': 'g/k', 'ㄴ': 'n', 'ㄷ': 'd/t', 'ㄹ': 'r/l',
        'ㅁ': 'm', 'ㅂ': 'b/p', 'ㅅ': 's', 'ㅇ': '', 
        'ㅈ': 'j', 'ㅊ': 'ch', 'ㅋ': 'k', 'ㅌ': 't',
        'ㅍ': 'p', 'ㅎ': 'h',
        'ㅏ': 'a', 'ㅑ': 'ya', 'ㅓ': 'eo', 'ㅕ': 'yeo',
        'ㅗ': 'o', 'ㅛ': 'yo', 'ㅜ': 'u', 'ㅠ': 'yu',
        'ㅡ': 'eu', 'ㅣ': 'i'
    }

    phonetic_transcription = ""
    for char in hangul_text:
        phonetic_transcription += phonetic_map.get(char, char)

    return phonetic_transcription

def analyze_grammar(text):
    """
    Appelle l'API LanguageTool pour analyser la grammaire.
    """
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
