from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from users.models import User

from .models import Conversation, Message
from .services import GeneratedResponse, StubGenerator, TransformersGenerator, get_generator, reset_generator_cache


class ChatBaselineTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="alice",
            password="A secure password 123!",
        )
        self.client.force_login(self.user)
        reset_generator_cache()

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

    def test_generator_backend_default_is_stub(self):
        reset_generator_cache()
        settings.M2_GENERATOR_BACKEND = "stub"
        generator = get_generator()
        self.assertEqual(generator.backend_name, "stub")

    def test_generator_cache_refreshes_after_backend_change(self):
        previous_backend = settings.M2_GENERATOR_BACKEND
        settings.M2_GENERATOR_BACKEND = "stub"
        reset_generator_cache()
        self.assertEqual(get_generator().backend_name, "stub")

        settings.M2_GENERATOR_BACKEND = "transformers"
        reset_generator_cache()
        self.assertEqual(get_generator().backend_name, "transformers")

        settings.M2_GENERATOR_BACKEND = previous_backend
        reset_generator_cache()

    def test_transformers_generator_is_instantiable_without_loading_model(self):
        generator = TransformersGenerator(model_name="test-model")
        self.assertEqual(generator.backend_name, "transformers")
        self.assertEqual(generator.model_name, "test-model")
        self.assertIsNone(generator._model)
        self.assertIsNone(generator._tokenizer)

    def test_generated_response_contract_is_coherent(self):
        response = GeneratedResponse(
            text="Réponse",
            model_name="stub-generator",
            backend="stub",
            sources=[],
            metadata={"messages_count": 1},
        )
        self.assertEqual(response.backend, "stub")
        self.assertEqual(response.metadata["messages_count"], 1)

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
