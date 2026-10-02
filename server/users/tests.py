import json

from django.test import TestCase

from .models import User


class AuthenticationTests(TestCase):
    def post_json(self, path, data):
        return self.client.post(
            path,
            data=json.dumps(data),
            content_type="application/json",
        )

    def test_complete_authentication_flow(self):
        password = "River!Window49Cloud"

        response = self.post_json(
            "/api/users/register/",
            {
                "full_name": "Test Citizen",
                "email": "citizen@example.com",
                "age": 22,
                "password": password,
            },
        )
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email="citizen@example.com")
        self.assertTrue(user.check_password(password))
        self.assertNotEqual(user.password, password)

        response = self.post_json(
            "/api/users/login/",
            {
                "email": user.email,
                "password": password,
            },
        )
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], user.id)

        response = self.post_json("/api/users/logout/", {})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            self.client.get("/api/users/me/").status_code,
            401,
        )

    def test_invalid_login(self):
        response = self.post_json(
            "/api/users/login/",
            {
                "email": "missing@example.com",
                "password": "WrongPassword",
            },
        )
        self.assertEqual(response.status_code, 400)

        self.assertEqual(
            self.client.get("/api/users/me/").status_code,
            401,
        )

    def test_invalid_registration(self):
        response = self.post_json(
            "/api/users/register/",
            {
                "full_name": "",
                "email": "invalid",
                "age": 12,
                "password": "",
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.exists())