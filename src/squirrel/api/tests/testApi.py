import json

from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
from squirrel.orders.models import Product


class ProductTests(APITestCase):
    def setUp(self) -> None:
        User.objects.create_user(username="any_user", password="test123")

        Product.objects.create(name="Apfel")
        Product.objects.create(name="Birne")
        Product.objects.create(name="Zurrgurt")

    def test_logged_out_forbidden(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 403)

    def test_logged_in_ok(self):
        self.client.login(username="any_user", password="test123")
        self.client.get("/api/products", format="json")

        response = self.client.get("/api/products/", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEquals(
            json.loads(response.content),
            {
                "count": 3,
                "next": None,
                "previous": None,
                "results": [
                    {"id": 1, "name": "Apfel", "unit": "Stück"},
                    {"id": 2, "name": "Birne", "unit": "Stück"},
                    {"id": 3, "name": "Zurrgurt", "unit": "Stück"},
                ],
            },
        )
