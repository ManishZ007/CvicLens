import json

from django.test import Client, TestCase

from .models import User


class AuthenticationTests(TestCase):
    def test_logout_requires_csrf_and_me_exposes_own_role(self):
        user = User.objects.create_user(email="staff-check@example.com", full_name="Staff", age=22,
                                        password="River!Window49Cloud", is_staff=True)
        client = Client(enforce_csrf_checks=True)
        client.force_login(user)
        self.assertTrue(client.get("/api/users/me/").json()["is_staff"])
        self.assertEqual(client.post("/api/users/logout/").status_code, 403)
        token = client.get("/api/complaints/csrf/").json()["csrfToken"]
        self.assertEqual(client.post("/api/users/logout/", HTTP_X_CSRFTOKEN=token).status_code, 200)
        self.assertEqual(client.get("/api/users/me/").status_code, 401)

    def post_json(self, path, data):
        return self.client.post(
            path, data=json.dumps(data), content_type="application/json"
        )

    def test_complete_authentication_flow(self):
        password = "River!Window49Cloud"
        response = self.post_json("/api/users/register/", {
            "full_name": "Test Citizen", "email": "citizen@example.com",
            "age": 22, "password": password,
        })
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email="citizen@example.com")
        self.assertTrue(user.check_password(password))
        self.assertNotEqual(user.password, password)
        response = self.post_json("/api/users/login/", {
            "email": user.email, "password": password,
        })
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/api/users/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], user.id)
        self.assertNotIn("password", response.json())
        self.assertEqual(self.post_json("/api/users/logout/", {}).status_code, 200)
        self.assertEqual(self.client.get("/api/users/me/").status_code, 401)

    def test_invalid_login(self):
        User.objects.create_user(
            email="citizen@example.com", password="River!Window49Cloud",
            full_name="Test Citizen", age=22,
        )
        response = self.post_json("/api/users/login/", {
            "email": "citizen@example.com", "password": "WrongPassword",
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.client.get("/api/users/me/").status_code, 401)

    def test_invalid_registration(self):
        response = self.post_json("/api/users/register/", {
            "full_name": "", "email": "invalid", "age": 12, "password": "",
        })
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.exists())
