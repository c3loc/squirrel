from decimal import Decimal

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import Permission, User
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.test import TestCase
from django.test.client import Client
from django.urls import resolve, reverse
from orders import views
from orders.models import Event, Order, Product, Team


def login(self):
    self.client = Client()
    self.user = User.objects.create_user("testuser", "user@example.com", "testpassword")
    self.client.login(username="testuser", password="testpassword")


# Tests in all classes shall be created in the order in which the
# paths are specified in urls.py
class RoutingTests(TestCase):
    """Test routing of all urlpatterns"""

    def test_root_resolves_overview(self):
        view = resolve("/")
        self.assertEqual(view.func, views.overview)

    def test_orders_resolves_orders(self):
        view = resolve("/orders")
        self.assertEqual(view.url_name, "orders")

    def test_order_resolves_order(self):
        view = resolve("/orders/23")
        self.assertEqual(view.func, views.order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"order_id": 23})

    def test_new_order_resolves_new_order(self):
        view = resolve("/orders/new")
        self.assertEqual(view.func, views.order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_delete_order_resolves_delete_order(self):
        view = resolve("/orders/delete/19")
        self.assertEqual(view.func, views.delete_order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"order_id": 19})

    def test_products_resolves_products(self):
        view = resolve("/products")
        self.assertEqual(view.url_name, "products")

    def test_product_resolves_product(self):
        view = resolve("/products/17")
        self.assertEqual(view.func, views.product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"product_id": 17})

    def test_new_product_resolves_new_product(self):
        view = resolve("/products/new")
        self.assertEqual(view.func, views.product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_delete_product_resolves_delete_product(self):
        view = resolve("/products/delete/12")
        self.assertEqual(view.func, views.delete_product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"product_id": 12})

    def test_teams_resolves_teams(self):
        view = resolve("/teams")
        self.assertEqual(view.url_name, "teams")

    def test_team_resolves_team(self):
        view = resolve("/teams/17")
        self.assertEqual(view.func, views.team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"team_id": 17})

    def test_new_team_resolves_new_team(self):
        view = resolve("/teams/new")
        self.assertEqual(view.func, views.team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_delete_team_resolves_delete_team(self):
        view = resolve("/teams/delete/12")
        self.assertEqual(view.func, views.delete_team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"team_id": 12})

    def test_budgets_resolves_budgets(self):
        view = resolve("/budgets")
        self.assertEqual(view.url_name, "budgets")


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

    def test_orders_status_code(self):
        """Order overview returns 200"""
        url = reverse("orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_orders_shows_new_button(self):
        """Order overview shows no orders when there are none"""
        url = reverse("orders")
        response = self.client.get(url)
        self.assertContains(response, "New Order</a>")

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

        Product.objects.create(name="Tardis", unit_price=17.00)

        Order.objects.create(
            amount=23,
            product=Product.objects.first(),
            team=Team.objects.first(),
            unit_price=13.57,
        )

    def test_inherit_product_price(self):
        product = Product.objects.first()

        product.unit_price = 23.03
        product.save()

        # This order has to change its unit_price as it’s not completed yet
        order_price_change = Order.objects.first()
        self.assertEqual(order_price_change.unit_price, Decimal("23.03"))


class OrderModelTests(TestCase):
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
        self.assertEqual(order.unit_price, Decimal("23.42"))

    def test_forbid_completed_order_deletion_or_update(self):
        order = Order.objects.first()

        order.state = "COM"
        order.save()

        # The order is now completed and must not be deleted
        self.assertRaises(PermissionDenied, order.delete())

        # The order must also not be changed once it’s completed
        order.amount = 1337
        self.assertRaises(PermissionDenied, order.save())


class TeamViewTests(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user("engel", password="engel")

        view_permission = Permission.objects.get(codename="view_team")
        user = User.objects.create_user("loc_engel", password="loc_engel")
        user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(codename="add_team")
        user = User.objects.create_user("order_engel", password="order_engel")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(add_permission)

        change_permission = Permission.objects.get(codename="change_team")
        user = User.objects.create_user("order_admin", password="order_admin")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(change_permission)

        delete_permission = Permission.objects.get(codename="delete_team")
        user = User.objects.create_user("morre", password="morre")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(delete_permission)

    def test_view_login_required(self):
        response = self.client.get("/teams")
        self.assertEqual(response.status_code, 302)

    def test_require_view_permissions_fails(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get("/teams")
        self.assertEqual(response.status_code, 403)

    def test_require_view_permissions_ok(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get("/teams")
        self.assertEqual(response.status_code, 200)

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.post("/teams/new", {"name": "Creatures"})
        self.assertEqual(response.status_code, 403)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post("/teams/new", {"name": "Creatures"})
        self.assertEqual(response.status_code, 302)

    def test_require_change_permission_fails(self):
        team = Team(name="BadWolf")
        team.save()
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post("/teams/{}".format(team.id), {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 403)

    def test_require_change_permission_ok(self):
        team = Team(name="BadWolf")
        team.save()
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/teams/{}".format(team.id), {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 302)

    def test_require_delete_permission_fails(self):
        team = Team(name="EvilTeam")
        team.save()
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/teams/delete/{}".format(team.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Team.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        team = Team(name="EvilTeam")
        team.save()
        self.client.login(username="morre", password="morre")
        response = self.client.post("/teams/delete/{}".format(team.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Team.objects.all().count(), 0)
