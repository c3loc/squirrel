from decimal import Decimal

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse
from orders.models import Event, Order, Product, Team
from orders.views import overview


def login(self):
    self.client = Client()
    self.user = User.objects.create_user("testuser", "user@example.com", "testpassword")
    self.client.login(username="testuser", password="testpassword")


# Tests in all classes shall be created in the order in which the
# paths are specified in urls.py
class RoutingTests(TestCase):
    """Test routing of all urlpatterns"""

    def test_root_resolves_overview_view(self):
        view = resolve("/")
        self.assertEqual(view.func, overview)


class NoOrderTests(TestCase):
    """Tests when there are no orders"""

    def setUp(self):
        Event.objects.create(name="TestEvent")

        login(self)

    def test_orders_status_code(self):
        """Order overview returns 200"""
        url = reverse("orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_empty_orders_shows_no_orders(self):
        """Order overview shows no orders when there are none"""
        url = reverse("orders")
        response = self.client.get(url)
        self.assertContains(response, "New Order</a>")


class OrderTests(TestCase):
    """Tests when there is at least one order"""

    def setUp(self):
        login(self)

        user_object = User.objects.create_user("TestUser")

        team_object = Team.objects.create(name="TestTeam",)
        team_object.members.add(1)  # TestUser has the ID 1

        event_object = Event.objects.create(name="TestEvent")

        product = Product.objects.create(name="Testprodukt",)

        Order.objects.create(
            amount="42",
            product=product,
            event=event_object,
            team=team_object,
            created_by=user_object,
        )

    def test_filled_orders_shows_orders(self):
        """Order overview does contain a link to existing order"""
        url = reverse("orders")

        response = self.client.get(url)
        self.assertContains(response, "Testprodukt")


class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse("password_reset")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset")
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)

    def test_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_contains_form(self):
        form = self.response.context.get("form")
        self.assertIsInstance(form, PasswordResetForm)

    def test_form_inputs(self):
        """The view must contain two inputs: csrf and email"""
        self.assertContains(self.response, "<input", 3)
        self.assertContains(self.response, 'type="email"', 1)


class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = "test@example.com"
        User.objects.create_user(
            username="test", email=email, password="ufgdlneginetriunae"
        )
        url = reverse("password_reset")
        self.response = self.client.post(url, {"email": email})

    def test_redirection(self):
        """A valid form submission should redirect the user to `password_reset_done` view"""
        url = reverse("password_reset_done")
        self.assertRedirects(self.response, url)

    def test_send_password_reset_email(self):
        self.assertEqual(1, len(mail.outbox))


class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse("password_reset")
        self.response = self.client.post(url, {"email": "donotexist@email.com"})

    def test_redirection(self):
        """Even invalid emails in the database should redirect the user to `password_reset_done` view"""
        url = reverse("password_reset_done")
        self.assertRedirects(self.response, url)

    def test_no_reset_email_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse("password_reset_done")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset/done")
        self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)


class ProductUpdateTests(TestCase):
    def setUp(self) -> None:
        # https://github.com/moby/moby/blob/3152f9436292115c97b4d8bb18c66cf97876ee75/pkg/namesgenerator/names-generator.go#L838-L840
        User.objects.create_user("Boring Wozniak")
        Team.objects.create(name="Aperture Science Laboratories")

        Product.objects.create(name="Tardis", unit_price=17.0042)
        Order.objects.create(
            amount=42,
            product=Product.objects.first(),
            team=Team.objects.first(),
            state="COM",
            unit_price=423.2312,
        )

        Order.objects.create(
            amount=23,
            product=Product.objects.first(),
            team=Team.objects.first(),
            unit_price=13.5731,
        )

    def test_inherit_product_price(self):
        product = Product.objects.first()

        product.unit_price = 23.0341
        product.save()

        # This order has to change its unit_price as it’s not completed yet
        order_price_change = Order.objects.get(amount=23)
        self.assertEqual(order_price_change.unit_price, Decimal("23.0341"))

        # This order is completed and must not change its unit_price
        order_no_price_change = Order.objects.get(amount=42)
        self.assertEqual(order_no_price_change.unit_price, Decimal("423.2312"))


class OrderCreateTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user("Wheatly")
        Team.objects.create(name="Aperture Science Laboratories")

        Product.objects.create(name="Dr. Cave Johnson", unit_price=23.42)
        Order.objects.create(
            product=Product.objects.first(), team=Team.objects.first(),
        )

    def test_inherit_product_price_on_create(self):
        order = Order.objects.first()

        # The order has to have the products unit_price as it was not specified on creation
        self.assertEqual(order.unit_price, Decimal("23.420"))
