from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from users.models import User

from .models import Conversation, Message
from .services import GeneratedResponse, StubGenerator, get_generator


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
            backend="stub",
            sources=[],
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

    def test_message_endpoint_rejects_invalid_json(self):
        response = self.client.post(
            reverse("chat:message"),
            data="not-json",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid JSON", response.json()["error"])

    def test_message_endpoint_rejects_empty_message(self):
        response = self.client.post(
            reverse("chat:message"),
            data={"message": "   "},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_message_endpoint_requires_authentication(self):
        self.client.logout()
        response = self.client.post(
            reverse("chat:message"),
            data={"message": "Bonjour"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_stub_backend_is_offline_and_deterministic(self):
        backend = StubGenerator()
        result = backend.generate(messages=[{"role": "user", "content": "Bonjour"}])
        self.assertEqual(result.backend, "stub")
        self.assertIn("Bonjour", result.text)
        self.assertEqual(result.sources, [])

    def test_generator_backend_selection_uses_settings(self):
        original = settings.M2_GENERATOR_BACKEND
        settings.M2_GENERATOR_BACKEND = "stub"
        try:
            generator = get_generator()
            self.assertEqual(generator.backend_name, "stub")
        finally:
            settings.M2_GENERATOR_BACKEND = original

    def test_can_reuse_existing_conversation_for_same_user(self):
        conversation = Conversation.objects.create(user=self.user)
        Message.objects.create(conversation=conversation, role=Message.Role.USER, content="Bonjour")

        response = self.client.post(
            reverse("chat:message"),
            data={"message": "Suite", "conversation_id": conversation.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["conversation_id"], conversation.id)

    def test_cannot_access_other_user_conversation(self):
        other_user = User.objects.create_user(username="bob", password="A secure password 123!")
        conversation = Conversation.objects.create(user=other_user)
        response = self.client.post(
            reverse("chat:message"),
            data={"message": "Bonjour", "conversation_id": conversation.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_context_is_limited_to_recent_messages(self):
        conversation = Conversation.objects.create(user=self.user)
        for idx in range(20):
            Message.objects.create(
                conversation=conversation,
                role=Message.Role.USER if idx % 2 == 0 else Message.Role.ASSISTANT,
                content=f"msg-{idx}",
            )
        response = self.client.post(
            reverse("chat:message"),
            data={"message": "dernier", "conversation_id": conversation.id},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("dernier", response.json()["response"])
