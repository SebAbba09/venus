from django.test import TestCase
from django.urls import reverse

from .models import User


class AuthenticationTests(TestCase):
    def test_registration_uses_django_password_hashing(self):
        response = self.client.post(
            reverse("users:register"),
            {
                "username": "alice",
                "password1": "A secure password 123!",
                "password2": "A secure password 123!",
            },
        )

        self.assertRedirects(response, reverse("chat:conversation"))
        user = User.objects.get(username="alice")
        self.assertTrue(user.check_password("A secure password 123!"))
        self.assertNotEqual(user.password, "A secure password 123!")
