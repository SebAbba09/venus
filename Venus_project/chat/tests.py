from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import Conversation, Message
from .services import GeneratedResponse


class ChatBaselineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            password="A secure password 123!",
        )
        self.client.force_login(self.user)

    @patch("chat.views.get_generator")
    def test_message_endpoint_persists_conversation_and_response(self, get_generator):
        get_generator.return_value.generate.return_value = GeneratedResponse(
            text="Réponse de baseline.",
            model_name="test-generator",
        )

        response = self.client.post(
            reverse("chat:message"),
            data={"message": "Bonjour"},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["response"], "Réponse de baseline.")
        conversation = Conversation.objects.get(user=self.user)
        self.assertEqual(
            list(conversation.messages.values_list("role", "content")),
            [
                (Message.Role.USER, "Bonjour"),
                (Message.Role.ASSISTANT, "Réponse de baseline."),
            ],
        )
