from django.contrib.auth.models import Permission, User
from django.test import TestCase
from orders.models import Order, Product, Team


class OrderFormTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(username="not_team_member", password="test123")

        self.user = User.objects.create_user(username="team_member", password="test123")
        self.team = Team.objects.create(name="Aperture Science Laboratories")
        self.team.members.add(self.user)
        self.team.save()

        helpdesk = User.objects.create_user(username="helpdesk", password="test123")
        helpdesk.user_permissions.add(Permission.objects.get(codename="view_team"))

        self.product = Product.objects.create(name="Tardis", unit_price=17.00)

    def test_require_amount(self):
        self.client.login(username="helpdesk", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "product": self.product.id,
                "team": self.team.id,
                "state": "REQ",
                "unit_price": 10.00,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<input type="number" name="amount" min="0" class="numberinput form-control is-invalid" required id="id_amount">',
            html=True,
        )

    def test_require_product_or_suggestion(self):
        self.client.login(username="helpdesk", password="test123")
        response = self.client.post(
            "/orders/new", {"team": self.team.id, "state": "REQ", "unit_price": 10.00}
        )
        self.assertEqual(response.status_code, 200)
        # this is a silent error.

    def test_require_state(self):
        self.client.login(username="helpdesk", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "unit_price": 10.00,
            },
        )
        self.assertEqual(response.status_code, 200)
        # TODO: why does this fail, but not the one below? something about the select?
        # self.assertContains(response, '<select name="state" class="select form-control is-invalid" id="id_state">', html=True)
        self.assertContains(
            response,
            b'<select name="state" class="select form-control is-invalid" id="id_state">',
        )

    def test_require_unit_price(self):
        self.client.login(username="helpdesk", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "state": "REQ",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<input type="number" name="unit_price" step="0.01" class="numberinput form-control is-invalid" required id="id_unit_price">',
            html=True,
        )

    def test_team_members_can_set_team(self):
        self.client.login(username="team_member", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "state": "REQ",
                "unit_price": 10.00,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.all().count(), 1)

    def test_non_team_members_can_not_set_team(self):
        self.client.login(username="not_team_member", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "state": "REQ",
                "unit_price": 10.00,
            },
        )
        self.assertEqual(response.status_code, 200)
        # TODO: why does this fail, but not the one below? something about the select?
        # self.assertContains(response, '<select name="team" class="select form-control is-invalid" required id="id_team">', html=True)
        self.assertContains(
            response,
            b'<select name="team" class="select form-control is-invalid" required id="id_team">',
        )

    def test_helpdesk_can_set_team(self):
        self.client.login(username="helpdesk", password="test123")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "state": "REQ",
                "unit_price": 10.00,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Order.objects.all().count(), 1)
