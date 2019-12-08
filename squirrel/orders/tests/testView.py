from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import resolve
from orders import views
from orders.models import Order, Product, Team


class RoutingTests(TestCase):
    """Test routing of all urlpatterns"""

    def test_root_resolves_overview(self):
        view = resolve("/")
        self.assertEqual(view.func, views.overview)
        self.assertEqual(view.url_name, "overview")

    def test_orders_resolves_orders(self):
        view = resolve("/orders")
        self.assertEqual(view.url_name, "orders")

    def test_new_order_resolves_new_order(self):
        view = resolve("/orders/new")
        self.assertEqual(view.func, views.order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_order_resolves_order(self):
        view = resolve("/orders/23")
        self.assertEqual(view.func, views.order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"order_id": 23})

    def test_delete_order_resolves_delete_order(self):
        view = resolve("/orders/delete/19")
        self.assertEqual(view.func, views.delete_order)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"order_id": 19})

    def test_products_resolves_products(self):
        view = resolve("/products")
        self.assertEqual(view.url_name, "products")

    def test_new_product_resolves_new_product(self):
        view = resolve("/products/new")
        self.assertEqual(view.func, views.product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_product_resolves_product(self):
        view = resolve("/products/17")
        self.assertEqual(view.func, views.product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"product_id": 17})

    def test_delete_product_resolves_delete_product(self):
        view = resolve("/products/delete/12")
        self.assertEqual(view.func, views.delete_product)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"product_id": 12})

    def test_teams_resolves_teams(self):
        view = resolve("/teams")
        self.assertEqual(view.url_name, "teams")

    def test_new_team_resolves_new_team(self):
        view = resolve("/teams/new")
        self.assertEqual(view.func, views.team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {})

    def test_team_resolves_team(self):
        view = resolve("/teams/17")
        self.assertEqual(view.func, views.team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"team_id": 17})

    def test_delete_team_resolves_delete_team(self):
        view = resolve("/teams/delete/12")
        self.assertEqual(view.func, views.delete_team)
        self.assertEqual(view.args, ())
        self.assertEqual(view.kwargs, {"team_id": 12})

    def test_budgets_resolves_budgets(self):
        view = resolve("/budgets")
        self.assertEqual(view.url_name, "budgets")


class OverviewViewTest(TestCase):
    def test_static_overview(self):
        response = self.client.get("/")
        self.assertContains(response, "Welcome to Squirrel")


class OrderViewTests(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user("engel", password="engel")

        team_permission = Permission.objects.get(codename="view_team")

        view_permission = Permission.objects.get(codename="view_order")
        user = User.objects.create_user("loc_engel", password="loc_engel")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(team_permission)

        add_permission = Permission.objects.get(codename="add_order")
        user = User.objects.create_user("order_engel", password="order_engel")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(add_permission)
        user.user_permissions.add(team_permission)

        change_permission = Permission.objects.get(codename="change_order")
        user = User.objects.create_user("order_admin", password="order_admin")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(change_permission)
        user.user_permissions.add(team_permission)

        delete_permission = Permission.objects.get(codename="delete_order")
        user = User.objects.create_user("morre", password="morre")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(delete_permission)
        user.user_permissions.add(team_permission)

        # https://github.com/moby/moby/blob/3152f9436292115c97b4d8bb18c66cf97876ee75/pkg/namesgenerator/names-generator.go#L838-L840
        self.team = Team.objects.create(name="Aperture Science Laboratories")
        self.product = Product.objects.create(name="Dr. Cave Johnson", unit_price=23.42)

        user = User.objects.create_user("team_member", password="team_member")
        self.team.members.add(user)

    def test_view_login_required(self):
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/orders")

    def test_no_orders_without_permission_or_membership(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<tbody></tbody>", html=True)

    def test_members_can_view_team_orders(self):
        my_order = Order.objects.create(product=self.product, team=self.team)
        order = Order.objects.create(
            product=self.product, team=Team.objects.create(name="Not My Team")
        )
        self.client.login(username="team_member", password="team_member")
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a class="btn btn-primary btn-sm" href="/orders/{}">'.format(my_order.id),
        )
        self.assertNotContains(
            response,
            '<a class="btn btn-primary btn-sm" href="/orders/{}">'.format(order.id),
        )

    def test_require_view_permissions_ok(self):
        my_order = Order.objects.create(product=self.product, team=self.team)
        order = Order.objects.create(product=self.product, team=self.team)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get("/orders")
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<a class="btn btn-primary btn-sm" href="/orders/{}">'.format(my_order.id),
        )
        self.assertContains(
            response,
            '<a class="btn btn-primary btn-sm" href="/orders/{}">'.format(order.id),
        )

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "unit_price": 1,
                "state": "REQ",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post(
            "/orders/new",
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "unit_price": 1,
                "state": "REQ",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/orders")
        self.assertEqual(Order.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        order = Order.objects.create(product=self.product, team=self.team)
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post(
            "/orders/{}".format(order.id),
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "unit_price": 1,
                "state": "REQ",
            },
        )
        self.assertEqual(response.status_code, 403)

    def test_require_change_permission_ok(self):
        order = Order.objects.create(product=self.product, team=self.team)
        order.save()
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post(
            "/orders/{}".format(order.id),
            {
                "amount": 1,
                "product": self.product.id,
                "team": self.team.id,
                "unit_price": 1,
                "state": "REQ",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/orders")

    def test_require_delete_permission_fails(self):
        order = Order.objects.create(product=self.product, team=self.team)
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/orders/delete/{}".format(order.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        order = Order.objects.create(product=self.product, team=self.team)
        self.client.login(username="morre", password="morre")
        response = self.client.post("/orders/delete/{}".format(order.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/orders")
        self.assertEqual(Order.objects.all().count(), 0)


class ProductViewTests(TestCase):
    def setUp(self) -> None:
        user = User.objects.create_user("engel", password="engel")

        view_permission = Permission.objects.get(codename="view_product")
        user = User.objects.create_user("loc_engel", password="loc_engel")
        user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(codename="add_product")
        user = User.objects.create_user("order_engel", password="order_engel")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(add_permission)

        change_permission = Permission.objects.get(codename="change_product")
        user = User.objects.create_user("order_admin", password="order_admin")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(change_permission)

        delete_permission = Permission.objects.get(codename="delete_product")
        user = User.objects.create_user("morre", password="morre")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(delete_permission)

    def test_view_login_required(self):
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/accounts/login/?next=/products")

    def test_require_view_permissions_fails(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 403)

    def test_require_view_permissions_ok(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get("/products")
        self.assertEqual(response.status_code, 200)

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.post(
            "/products/new",
            {"name": "Awesome Beer", "unit": "Hectoliter", "unit_price": "5"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post(
            "/products/new",
            {"name": "Awesome Beer", "unit": "Hectoliter", "unit_price": "5"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/products")
        self.assertEqual(Product.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post(
            "/products/{}".format(product.id),
            {"name": "Awesome Beer", "unit": "Hectoliter", "unit_price": "5"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.get(id=product.id).name, "Bad Beer")

    def test_require_change_permission_ok(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post(
            "/products/{}".format(product.id),
            {"name": "Awesome Beer", "unit": "Hectoliter", "unit_price": "5"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/products")
        self.assertEqual(Product.objects.get(id=product.id).name, "Awesome Beer")

    def test_require_delete_permission_fails(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/products/delete/{}".format(product.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="morre", password="morre")
        response = self.client.post("/products/delete/{}".format(product.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/products")
        self.assertEqual(Product.objects.all().count(), 0)


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
        self.assertEqual(response.url, "/accounts/login/?next=/teams")

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
        self.assertEqual(Team.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post("/teams/new", {"name": "Creatures"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/teams")
        self.assertEqual(Team.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        team = Team.objects.create(name="BadWolf")
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post("/teams/{}".format(team.id), {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 403)

    def test_require_change_permission_ok(self):
        team = Team.objects.create(name="BadWolf")
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/teams/{}".format(team.id), {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/teams")

    def test_require_delete_permission_fails(self):
        team = Team.objects.create(name="EvilTeam")
        self.client.login(username="order_admin", password="order_admin")
        response = self.client.post("/teams/delete/{}".format(team.id))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Team.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        team = Team.objects.create(name="EvilTeam")
        self.client.login(username="morre", password="morre")
        response = self.client.post("/teams/delete/{}".format(team.id))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/teams")
        self.assertEqual(Team.objects.all().count(), 0)
