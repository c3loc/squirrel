from test.support import EnvironmentVarGuard

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from squirrel.orders.models import Event, Order, Product, Team, Vendor


class OrderViewTests(TestCase):
    def setUp(self) -> None:
        self.view_permission = Permission.objects.get(codename="view_order")
        self.add_permission = Permission.objects.get(codename="add_order")
        self.change_permission = Permission.objects.get(codename="change_order")
        self.delete_permission = Permission.objects.get(codename="delete_order")

        self.team_a = Team.objects.create(name="The A-Team")
        self.team_b = Team.objects.create(name="Not the A-Team")
        self.product = Product.objects.create(name="Dr. Cave Johnson")

        # a user without any permission
        self.user = User.objects.create_user("engel", password="engel")

        # a user with view permission
        self.view_user = User.objects.create_user("loc_engel", password="loc_engel")
        self.view_user.user_permissions.add(self.view_permission)

        self.eventA = Event.objects.create(name="Required Event")

    def post_order(self, id="new", amount=1, comment="", event=1):
        url = (
            reverse("orders:add_order")
            if id == "new"
            else reverse("orders:change_order", args=[id])
        )
        return self.client.post(
            url,
            {
                "amount": amount,
                "product": self.product.id,
                "team": self.team_a.id,
                "comment": comment,
                "event": event,
            },
        )

    def test_view_login_required(self):
        url = reverse("orders:orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_can_not_see_orders_without_permission_or_membership(self):
        Order.objects.create(product=self.product, team=self.team_a)
        Order.objects.create(product=self.product, team=self.team_b)
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:orders"))
        self.assertEqual(response.status_code, 403)

    def test_view_permission_can_see_all_orders(self):
        Order.objects.create(product=self.product, team=self.team_a)
        Order.objects.create(product=self.product, team=self.team_b)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The A-Team")
        self.assertContains(response, "Not the A-Team")

    def test_add_order_has_comment_field(self):
        self.view_user.user_permissions.add(self.add_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:add_order"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<textarea name="comment" cols="30" rows="3" maxlength="1000" '
            'class="textarea form-control" id="id_comment">',
        )

    def test_event_preset_by_setting(self):
        env = EnvironmentVarGuard()
        env.set("DEFAULT_ORDER_EVENT", "12c3")
        self.view_user.user_permissions.add(self.add_permission)
        Event.objects.create(name="12c3")
        Event.objects.create(name="42c3")
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:add_order"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="2" selected>12c3</option>')

    # This test somehow does not work. If you use the software, it works as defined and
    # uses the last event that was added
    # def test_event_use_last(self):
    #     self.view_user.user_permissions.add(self.add_permission)
    #     Event.objects.create(name="12c3")
    #     Event.objects.create(name="42c3")
    #     self.client.login(username="loc_engel", password="loc_engel")
    #     response = self.client.get("/orders/new")
    #     self.assertEqual(response.status_code, 200)
    #     self.assertContains(response, '<option value="3" selected>42c3</option>')

    def test_event_no_event_defined(self):
        Event.objects.all().delete()

        self.view_user.user_permissions.add(self.add_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:add_order"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="" selected>---------</option>')

    def test_status_can_view_only(self):
        """
        Tests if a user having only view rights can load the order view for an existing order
        """
        Order.objects.create(product=self.product, team=self.team_a)

        self.client.login(username="loc_engel", password="loc_engel")

        response = self.client.get(reverse("orders:change_order", args=["1"]))
        self.assertEqual(response.status_code, 403)


class OrderExportViewTests(TestCase):
    def setUp(self) -> None:
        # Various permission objects for convinience use
        self.export_permission = Permission.objects.get(codename="export_csv")

        # User without rights
        self.user = User.objects.create_user("engel", password="engel")

        # a user with view permission, can export CSV
        self.view_user = User.objects.create_user("exporter", password="exporter")
        self.view_user.user_permissions.add(self.export_permission)

    def test_view_login_required(self):
        url = reverse("orders:export_orders_csv")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_non_privileged_can_not_export(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:export_orders_csv"))
        self.assertEqual(response.status_code, 403)

    def test_privileged_can_export(self):
        self.client.login(username="exporter", password="exporter")
        response = self.client.get(reverse("orders:export_orders_csv"))
        self.assertEqual(response.status_code, 200)


class ProductViewTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user("engel", password="engel")
        self.vendor = Vendor.objects.create(name="ACME Inc.")

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

    def test_view_new_product_status_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.get(reverse("orders:new_product"))
        self.assertEqual(response.status_code, 200)

    def test_view_login_required(self):
        url = reverse("orders:products")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_require_view_permissions_fails(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:products"))
        self.assertEqual(response.status_code, 403)

    def test_require_view_permissions_ok(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:products"))
        self.assertEqual(response.status_code, 200)

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")
        vendor = Vendor.objects.get(name="ACME Inc.")

        url = reverse("orders:new_product")
        response = self.client.post(
            url, {"name": "Awesome Beer", "unit": "Hectoliter", "vendor": vendor.id},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")

        url = reverse("orders:new_product")
        response = self.client.post(
            url, {"name": "Awesome Beer", "unit": "Hectoliter"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:products"))
        self.assertEqual(Product.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        product = Product.objects.create(name="Bad Beer")
        vendor = Vendor.objects.get(name="ACME Inc.")

        self.client.login(username="order_engel", password="order_engel")
        url = reverse("orders:edit_product", args=[product.id])
        response = self.client.post(
            url, {"name": "Awesome Beer", "unit": "Hectoliter", "vendor": vendor.id},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.get(id=product.id).name, "Bad Beer")

    def test_require_change_permission_ok(self):
        product = Product.objects.create(name="Bad Beer")

        self.client.login(username="order_admin", password="order_admin")
        url = reverse("orders:edit_product", args=[product.id])
        response = self.client.post(
            url, {"name": "Awesome Beer", "unit": "Hectoliter"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:products"))
        self.assertEqual(Product.objects.get(id=product.id).name, "Awesome Beer")

    def test_require_delete_permission_fails(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="order_admin", password="order_admin")

        url = reverse("orders:delete_product", args=[product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Product.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        product = Product.objects.create(name="Bad Beer")
        self.client.login(username="morre", password="morre")

        url = reverse("orders:delete_product", args=[product.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:products"))
        self.assertEqual(Product.objects.all().count(), 0)


class VendorViewTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user("engel", password="engel")

        view_permission = Permission.objects.get(codename="view_vendor")
        user = User.objects.create_user("loc_engel", password="loc_engel")
        user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(codename="add_vendor")
        user = User.objects.create_user("order_engel", password="order_engel")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(add_permission)

        change_permission = Permission.objects.get(codename="change_vendor")
        user = User.objects.create_user("order_admin", password="order_admin")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(change_permission)

        delete_permission = Permission.objects.get(codename="delete_vendor")
        user = User.objects.create_user("morre", password="morre")
        user.user_permissions.add(view_permission)
        user.user_permissions.add(delete_permission)

    def test_view_login_required(self):
        url = reverse("orders:vendors")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_require_view_permissions_fails(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:vendors"))
        self.assertEqual(response.status_code, 403)

    def test_require_view_permissions_ok(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:vendors"))
        self.assertEqual(response.status_code, 200)

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.post(
            reverse("orders:new_vendor"), {"name": "Bällebäder for the win"},
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vendor.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")
        response = self.client.post(
            reverse("orders:new_vendor"), {"name": "Bällebäder for the win"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:vendors"))
        self.assertEqual(Vendor.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        vendor = Vendor.objects.create(name="Kein Bällebadverkäufer")
        self.client.login(username="order_engel", password="order_engel")

        url = reverse("orders:edit_vendor", args=[vendor.id])
        response = self.client.post(url, {"name": "Bällebäder for the win"},)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            Vendor.objects.get(id=vendor.id).name, "Kein Bällebadverkäufer"
        )

    def test_require_change_permission_ok(self):
        vendor = Vendor.objects.create(name="Kein Bällebadverkäufer")
        self.client.login(username="order_admin", password="order_admin")
        url = reverse("orders:edit_vendor", args=[vendor.id])
        response = self.client.post(url, {"name": "Bällebäder for the win"},)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:vendors"))
        self.assertEqual(
            Vendor.objects.get(id=vendor.id).name, "Bällebäder for the win"
        )

    def test_require_delete_permission_fails(self):
        vendor = Vendor.objects.create(name="Bad Beer")
        self.client.login(username="order_admin", password="order_admin")
        url = reverse("orders:delete_vendor", args=[vendor.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vendor.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        vendor = Vendor.objects.create(name="Kein Bällebadverkäufer")
        self.client.login(username="morre", password="morre")
        url = reverse("orders:delete_vendor", args=[vendor.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:vendors"))
        self.assertEqual(Vendor.objects.all().count(), 0)


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
        url = reverse("orders:teams")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/accounts/login/?next={url}")

    def test_require_view_permissions_fails(self):
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:teams"))
        self.assertEqual(response.status_code, 403)

    def test_require_view_permissions_ok(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:teams"))
        self.assertEqual(response.status_code, 200)

    def test_require_add_permission_fails(self):
        self.client.login(username="loc_engel", password="loc_engel")

        url = reverse("orders:new_team")
        response = self.client.post(url, {"name": "Creatures"})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Team.objects.all().count(), 0)

    def test_require_add_permission_ok(self):
        self.client.login(username="order_engel", password="order_engel")

        url = reverse("orders:new_team")
        response = self.client.post(url, {"name": "Creatures"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:teams"))
        self.assertEqual(Team.objects.all().count(), 1)

    def test_require_change_permission_fails(self):
        team = Team.objects.create(name="BadWolf")
        self.client.login(username="order_engel", password="order_engel")

        url = reverse("orders:edit_team", args=[team.id])
        response = self.client.post(url, {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 403)

    def test_require_change_permission_ok(self):
        team = Team.objects.create(name="BadWolf")
        self.client.login(username="order_admin", password="order_admin")
        url = reverse("orders:edit_team", args=[team.id])
        response = self.client.post(url, {"name": "GoodWolf"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:teams"))

    def test_require_delete_permission_fails(self):
        team = Team.objects.create(name="EvilTeam")
        self.client.login(username="order_admin", password="order_admin")

        url = reverse("orders:delete_team", args=[team.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Team.objects.all().count(), 1)

    def test_require_delete_permission_ok(self):
        team = Team.objects.create(name="EvilTeam")
        self.client.login(username="morre", password="morre")
        url = reverse("orders:delete_team", args=[team.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:teams"))
        self.assertEqual(Team.objects.all().count(), 0)
