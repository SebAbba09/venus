# services.py
from textblob import TextBlob
import requests
from translate import Translator
from transformers import BlenderbotForConditionalGeneration, BlenderbotTokenizer
import torch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(
    "D:/Download/HugginFace/VenusChatbot/Venus_project/static/blender_train")


def translate_to_french(text):
    translator = Translator(to_lang="fr")
    translation = translator.translate(text)
    return translation


def analyze_sentiment(text):
    """
    Analyse le sentiment d'un texte.
    """
    sentiment_dict = analyzer.polarity_scores(text)
    return sentiment_dict['compound'], sentiment_dict['pos'], sentiment_dict['neu'], sentiment_dict['neg']


def process_message(user_message):
    # Traduire le message utilisateur en français
    french_message = translate_to_french(user_message)

    # Générer la réponse du chatbot en utilisant le message traduit
    chatbot_response = generate_chatbot_response(french_message)

    # Traduire la réponse du chatbot en français (si nécessaire)
    french_response = translate_to_french(chatbot_response)

    return french_response


Translator = Translator()
analyzer = SentimentIntensityAnalyzer()


def generate_chatbot_response(french_message):
    """
    Génère une réponse du chatbot à partir d'un message en français.
    """
    try:
        # Traduire le message en anglais si le message est en français
        english_message = Translator.translate(french_message, dest='en').text

        # Préparer l'entrée pour le modèle
        input_ids = tokenizer.encode(english_message, return_tensors="pt")

        # Générer la réponse du modèle
        with torch.no_grad():
            bot_output = model.generate(input_ids, max_length=150, num_beams=5, no_repeat_ngram_size=2)

        # Décoder la réponse du modèle
        bot_reply = tokenizer.decode(bot_output[0], skip_special_tokens=True)

        # Analyser le sentiment du message
        sentiment_score, pos, neu, neg = analyze_sentiment(english_message)

        # Ajouter une réponse sentimentale
        if sentiment_score >= 0.05:
            sentiment_response = "Je suis content que vous soyez de bonne humeur!"
        elif sentiment_score <= -0.05:
            sentiment_response = "Je suis désolé que vous ne vous sentiez pas bien. Je suis là pour vous aider."
        else:
            sentiment_response = "Merci pour votre message!"

        # Combiner la réponse du modèle avec la réponse sentimentale
        full_reply = f"{bot_reply} {sentiment_response}"

        # Traduire la réponse complète en français
        french_reply = Translator.translate(full_reply, dest='fr').text

        return french_reply
    except Exception as e:
        return f"An error occurred: {str(e)}"


def process_personalized_message_with_context(user_message, context, preferences):
    if 'name' in preferences:
        response = f"Bonjour {preferences['name']} ! Comment puis-je vous aider aujourd'hui ?"
    else:
        response = "Bonjour ! Comment vous appelez-vous ?"

    # Mettre à jour les préférences utilisateur
    if "je m'appelle" in user_message.lower():
        preferences['name'] = user_message.split("je m'appelle ")[1]

    # Utiliser le contexte pour traiter le message
    if 'favorite_food' in context:
        response += f" Je me souviens que vous aimez {context['favorite_food']}. Voulez-vous en parler davantage ?"
    else:
        response += " Pouvez-vous me parler de vos goûts alimentaires ?"

    # Mettre à jour le contexte
    if "j'aime" in user_message.lower():
        context['favorite_food'] = user_message.split("j'aime ")[1]

    return response, context, preferences


#permet de generer des recommandations
def generate_recommendations(preferences):
    # Exemple fictif : générer des recommandations basées sur les préférences utilisateur
    recommendations = []
    if 'favorite_hobby' in preferences:
        recommendations.append(f"Passez du temps à {preferences['favorite_hobby']} aujourd'hui.")

    if 'favorite_food' in preferences:
        recommendations.append(f"Vous pourriez aimer le restaurant qui sert {preferences['favorite_food']}.")

    if 'favorite_movie' in preferences:
        recommendations.append(f"Un nouveau film similaire à {preferences['favorite_movie']} est sorti récemment.")
    return recommendations


#ici je vais implementer une fonction permettant d'analyser les sentiments de l'user et renvoyer un truc
def analyze_sentiment(message):
    blob = TextBlob(message)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return 'positive'
    elif sentiment < 0:
        return 'negative'
    else:
        return 'neutral'


def get_encouraging_quote():
    response = requests.get("https://api.quotable.io/random")
    if response.status_code == 200:
        data = response.json()
        return data['content']
    return "Gardez le sourire, les choses vont s'améliorer!"


def process_personalized_message_with_context_and_sentiment(user_message, context, preferences, sentiment):
    response = ""
    if sentiment == 'negative':
        response = get_encouraging_quote()
    else:
        if 'name' in preferences:
            response = f"Bonjour {preferences['name']} ! Comment puis-je vous aider aujourd'hui ?"
        else:
            response = "Bonjour ! Comment vous appelez-vous ?"

        if "je m'appelle" in user_message.lower():
            preferences['name'] = user_message.split("je m'appelle ")[1]

        if 'favorite_food' in context:
            response += f" Je me souviens que vous aimez {context['favorite_food']}. Voulez-vous en parler davantage ?"
        else:
            response += " Pouvez-vous me parler de vos goûts alimentaires ?"

        if "j'aime" in user_message.lower():
            context['favorite_food'] = user_message.split("j'aime ")[1]

    return response, context, preferences
