# Venus/views.py
import random

import requests
import torch
import json

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.template import loader

from translate import Translator
from django.utils.translation import gettext_lazy as _
from googletrans import Translator, LANGUAGES

from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from transformers import BlenderbotTokenizer, BlenderbotForConditionalGeneration
from django.views.decorators.http import require_http_methods

from django.conf import settings

from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login as auth_login, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm, \
    AuthenticationForm
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.contrib import messages

from django.templatetags.static import static
from django.views.decorators.csrf import csrf_protect

from .chatbot import get_chatbot_response  # Importez la fonction depuis chatbot.py
from django.utils import timezone
from .forms import (CustomPasswordChangeForm, EventForm, CustomAuthenticationForm,
                    CustomSetPasswordForm, CustomPasswordResetForm, CustomUserCreationForm)
from .models import (UserContext, UserProfile, CustomUser, Password,
                     CustomUserManager, Event, )

from .services import (process_message, process_personalized_message_with_context,
                       generate_recommendations, process_personalized_message_with_context_and_sentiment,
                       analyze_sentiment, get_encouraging_quote, translate_to_french,
                       generate_chatbot_response)

model_name = "facebook/blenderbot-400M-distill"
tokenizer = BlenderbotTokenizer.from_pretrained(model_name)
model = BlenderbotForConditionalGeneration.from_pretrained(
    "D:/Download/HugginFace/VenusChatbot/Venus_project/static/blender_train")

# Initialise le traducteur pour la traduction en français
#translator_to_fr = Translator(to_lang='fr')
#translator_to_en = Translator(to_lang='en')
# Créer une instance du traducteur
translator = Translator()


@csrf_exempt
def translate(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        text = data.get('text', '')
        use_local_translation = data.get('use_local', False)

        if use_local_translation:
            translated_text = local_translate(text)
        else:
            translated_text = translate_with_mymemory(text)

        return JsonResponse({'translated_text': translated_text})

    return JsonResponse({'error': 'Invalid request method'}, status=400)


def translate_text(text, target_language='fr'):
    """
    Traduire le texte en utilisant googletrans.

    :param text: Texte à traduire
    :param target_language: Langue cible pour la traduction (par exemple, 'fr' pour le français)
    :return: Texte traduit
    """
    try:
        # Effectuer la traduction
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        # En cas d'erreur, afficher l'erreur et retourner le texte original
        print(f"Erreur lors de la traduction: {e}")
        return text


def local_translate(text):
    translations = {
        "hello": "bonjour",
        "world": "monde",
    }
    words = text.lower().split()
    translated_words = [translations.get(word, word) for word in words]
    return ' '.join(translated_words)


def translate_with_mymemory(text, langpair='en|fr'):
    url = "https://api.mymemory.translated.net/get"
    params = {
        'q': text,
        'langpair': langpair
    }
    response = requests.get(url, params=params)
    data = response.json()
    if 'responseData' in data:
        return data['responseData']['translatedText']
    else:
        return "Translation failed."


def test_view(request):
    return HttpResponse("Test page accessible via HTTP")


#code pour l'accueil
def accueil(request):
    return render(request, 'accueil.html')


#CODE POUR LAVATAR

def avatar_gallery(request):
    template = loader.get_template('select_avatar.html')
    names = ['Callie', 'Gizmo', 'Harley', 'Buddy', 'Buster', 'Smokey', 'Muffin', 'Annie', 'Lily',
             'Angel', 'Chloe', 'Midnight', 'Oliver', 'Mia', 'Bear', 'Leo', 'Max', 'Toby', 'Jasper', 'Kiki']
    selected_avatar = 'Callie'

    if request.method == 'POST':
        selected_avatar = request.POST.get('avatar', 'Callie')
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.avatar = selected_avatar
        user_profile.save()
        return redirect('chat_view')  # Redirige vers le chatbot après la sélection de l'avatar

    context = {
        'names': names,
        'selected_avatar': selected_avatar
    }

    return HttpResponse(template.render(context, request))


def validate_avatar(request):
    if request.method == 'POST':
        selected_avatar = request.POST.get('avatar')
        request.session['selected_avatar'] = selected_avatar
        return redirect('chat_form')


#code pour s'inscrire
def login(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Spécifiez le backend à utiliser pour l'authentification
            backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user, backend=backend)  # Connecte automatiquement l'utilisateur après l'inscription
            return redirect('merci')  # Redirige vers la page de remerciement

        else:
            # Si le formulaire n'est pas valide, afficher les erreurs
            for error in form.errors.values():
                messages.error(request, error)
    else:
        form = CustomUserCreationForm()

    return render(request, 'login.html', {'form': form})


#code pour faire la connexion
def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Assurez-vous que le backend d'authentification est défini
            backend = 'django.contrib.auth.backends.ModelBackend'
            auth_login(request, user,
                       backend=backend)  # Connecte automatiquement l'utilisateur après l'authentification
            return redirect('accueil')  # Redirige vers la galerie d'avatars après connexion
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect')
    else:
        form = AuthenticationForm()

    return render(request, 'connexion.html', {'form': form})


#code pour reset le mot de passe
def password_reset_request(request):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = get_object_or_404(User, email=email)
            token = default_token_generator.make_token(user)
            uid = user.pk
            reset_link = request.build_absolute_uri(
                reverse('password_reset_confirm_view', kwargs={'uidb64': uid, 'token': token})
            )
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_link}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            return redirect('password_change_view')
    else:
        form = PasswordResetForm()
    return render(request, 'password_reset_request.html', {'form': form})


#vue pour la confirmation de la reinitialisation du mot de passe

def password_reset_confirm_view(request, uidb64=None, token=None):
    try:
        user = CustomUser.objects.get(pk=uidb64)
    except CustomUser.DoesNotExist:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('password_reset_confirm_view')
        else:
            form = SetPasswordForm(user=user)
    else:
        form = None

    return render(request, 'password_reset_confirm.html', {'form': form})


#vue pour le changement de mot de passe

@login_required
def password_change_view(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Maintenir la session active
            return redirect('password_change_done_view')
    else:
        form = CustomPasswordChangeForm(user=request.user)
    return render(request, 'password_chang_form.html', {'form': form})


#vue pour valider le changement de mot de passe
@login_required
def password_change_done_view(request):
    return render(request, 'mdp.html')


#un code pour un ecran de remerciement, une fois l'inscription valider
def merci(request):
    return render(request, 'merci.html')


#code pour le contact
def contact(request):
    if request.method == 'POST':
        username = request.POST['username']
        question = request.POST['question']
        # Traitez ici les données du formulaire selon vos besoins
        # ...
        # Après traitement, redirigez l'utilisateur vers la page d'accueil
        return redirect('accueil')
    return render(request, 'contact.html')


#code pour le mot de passe

def mdp(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('new_password')
        if new_password == confirm_password:
            try:
                user = CustomUser.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                # Store the password in the Password model
                Password.objects.create(user=user, password=new_password)
                return redirect('login')
            except CustomUser.DoesNotExist:
                return render(request, 'mdp.html', {'error': 'User does not exist'})
        else:
            return render(request, 'mdp.html', {'error': 'Passwords do not match'})
    return render(request, 'mdp.html')


#partie de MON CODE

# Simule un stockage temporaire de l'historique de la conversation
conversation_history = []


@require_http_methods(["GET", "POST"])
@csrf_protect
def chat_view(request):
    global conversation_history

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '')
            translate_to_french = data.get('translate_to_french', 'false') == 'true'
            translate_conversation = data.get('translate_conversation', 'false') == 'true'

            if translate_conversation:
                # Traduire toute la conversation en cours
                translated_history = []
                for entry in conversation_history:
                    translated_entry = {
                        'user_message': translate_text(entry['user_message'], target_language='fr'),
                        'bot_response': translate_text(entry['bot_response'], target_language='fr')
                    }
                    translated_history.append(translated_entry)
                return JsonResponse({'conversation': translated_history})

            if user_message.strip():
                # Ajout du message utilisateur à l'historique
                conversation_history.append({'user_message': user_message, 'bot_response': ''})

                # Préparer les entrées pour le modèle
                inputs = tokenizer(user_message, return_tensors='pt')
                reply_ids = model.generate(**inputs, max_length=250)
                bot_response = tokenizer.decode(reply_ids[0], skip_special_tokens=True)

                # Ajout de la réponse du bot à l'historique
                conversation_history[-1]['bot_response'] = bot_response

                # Traduire la réponse du modèle en français si nécessaire
                if translate_to_french:
                    bot_response = translate_text(bot_response, target_language='fr')

                return JsonResponse({'response': bot_response})
            else:
                return JsonResponse({'response': 'Erreur: Message vide.'}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'response': 'Erreur: Données invalides.'}, status=400)
        except Exception as e:
            print(f"Erreur: {str(e)}")
            return JsonResponse({'response': f'Erreur: {str(e)}'}, status=500)
    elif request.method == 'GET':
        return JsonResponse({'message': 'Utilisez une requête POST pour envoyer un message au chatbot.'})
    else:
        return JsonResponse({'response': 'Erreur: Méthode non autorisée.'}, status=405)


def chat_form(request):
    default_avatar_url = static('casper.jpg')
    selected_avatar = request.session.get('selected_avatar', default_avatar_url)

    return render(request, 'chat_form.html', {
        'selected_avatar': selected_avatar,
    })


def home(request):
    return render(request, 'home.html')  #


#fonction permettant de gerer la traduction des messages


@csrf_exempt
def chat_poll(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        message = data.get('message', '')
        response = get_chatbot_response(message)  # Appelle la fonction du modèle
        return JsonResponse({'response': response})
    return JsonResponse({'error': 'Invalid request'}, status=400)


@csrf_exempt
def chat_view_with_context(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        user_id = request.session.session_key

        # Récupérer ou initialiser le contexte de l'utilisateur
        context, created = UserContext.objects.get_or_create(user_id=user_id)

        # Récupérer ou initialiser le profil de l'utilisateur
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)

        # Générer la réponse du chatbot en utilisant le contexte et les préférences utilisateur
        response, updated_context, updated_preferences = process_personalized_message_with_context(user_message,
                                                                                                   context.context,
                                                                                                   profile.preferences)

        # Générer des recommandations
        recommendations = generate_recommendations(updated_preferences)

        # Mettre à jour le contexte de l'utilisateur
        context.context = updated_context
        context.save()

        # Mettre à jour les préférences utilisateur
        profile.preferences = updated_preferences
        profile.recommendations = recommendations
        profile.save()

        return JsonResponse({'response': response, 'recommendations': recommendations})
    return render(request, 'chat.html')


#cette partie permettra de gerer les notifications


# Exemple d'ajout de notification dans une vue existante
def chat_view_with_notifications(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        user_id = request.session.session_key

        # Récupérer ou initialiser le contexte de l'utilisateur
        context, created = UserContext.objects.get_or_create(user_id=user_id)

        # Récupérer ou initialiser le profil de l'utilisateur
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)

        # Analyser le sentiment
        sentiment = analyze_sentiment(user_message)

        # Processus de message personnalisé avec traduction et analyse de sentiment
        response, updated_context, updated_preferences = process_personalized_message_with_context_and_sentiment(
            user_message, context.context, profile.preferences, sentiment)

        # Générer des recommandations
        recommendations = generate_recommendations(updated_preferences)

        # Mettre à jour le contexte de l'utilisateur
        context.context = updated_context
        context.save()

        # Mettre à jour les préférences utilisateur
        profile.preferences = updated_preferences
        profile.recommendations = recommendations
        profile.save()

        # Envoyer une notification

        return JsonResponse({'response': response, 'recommendations': recommendations, 'sentiment': sentiment})
    return render(request, 'chat.html')


def personalized_chat_with_sentiment_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message')
        user_id = request.session.session_key

        context, created = UserContext.objects.get_or_create(user_id=user_id)
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)

        sentiment = analyze_sentiment(user_message)

        response, updated_context, updated_preferences = process_personalized_message_with_context_and_sentiment(
            user_message, context.context_data, profile.preferences, sentiment)

        recommendations = generate_recommendations(updated_preferences)

        context.context_data = updated_context
        context.save()

        profile.preferences = updated_preferences
        profile.save()

        return JsonResponse({'response': response, 'recommendations': recommendations, 'sentiment': sentiment})
    return render(request, 'chat.html')


# code pour gerer l'agenda

# @login_required
def add_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user = request.user
            event.save()
            return redirect('calendar')
    else:
        form = EventForm()
    return render(request, 'add_event.html', {'form': form})


#@login_required
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('chat')
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form})


@csrf_exempt
def update_event(request, event_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        event = Event.objects.get(id=event_id)
        event.title = data['title']
        event.description = data['description']
        event.start_time = data['start_time']
        event.end_time = data['end_time']
        event.save()
        return JsonResponse({'status': 'success'})


#V@login_required
def delete_event(request, event_id):
    event = Event.objects.get(id=event_id)
    if event.user == request.user:
        event.delete()
    return redirect('chat')


# @login_required
def event_list(request):
    """
    Vue pour afficher la liste des événements de l'utilisateur connecté.

    - Récupère les événements associés à l'utilisateur actuellement connecté.
    - Rend la page 'event_list.html' avec la liste des événements.
    """
    # Récupérer les événements de l'utilisateur connecté
    events = Event.objects.filter(User=request.User)

    # Passer les événements au modèle
    return render(request, 'event_list.html', {'events': events})
