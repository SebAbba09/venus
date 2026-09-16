# Venus/translation.py

from googletrans import Translator

def translate_message(message, target_language='en'):
    translator = Translator()
    translated = translator.translate(message, dest=target_language)
    return translated.text
