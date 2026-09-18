from django.test import TestCase

# Create your tests here.

from translate import Translator

def translate_to_french(text):
    # Créez un traducteur pour la langue source (ici, 'auto' pour détecter automatiquement) vers le français
    translator = Translator(to_lang="fr")
    # Traduisez le texte
    translation = translator.translate(text)
    return translation

# Exemple d'utilisation
user_input = "Hello, how are you?"  # Texte d'entrée de l'utilisateur
translated_text = translate_to_french(user_input)  # Traduction en français
print(translated_text)  # Affiche le texte traduit

