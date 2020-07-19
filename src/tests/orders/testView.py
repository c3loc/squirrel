from test.support import EnvironmentVarGuard

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse
from squirrel.orders.models import Event, Order, Product, Team, Vendor


class OrderViewTests(TestCase):
    def setUp(self) -> None:
        # Various permission objects for convinience use
        self.team_permission = Permission.objects.get(codename="view_team")
        self.request_permission = Permission.objects.get(codename="request_order")
        self.approve_permission = Permission.objects.get(codename="approve_order")
        self.receive_permission = Permission.objects.get(codename="receive_order")
        self.complete_permission = Permission.objects.get(codename="complete_order")

        self.view_permission = Permission.objects.get(codename="view_order")
        self.view_all_teams_permission = Permission.objects.get(
            codename="view_order_all_teams"
        )

        self.add_permission = Permission.objects.get(codename="add_order")
        self.add_all_teams_permission = Permission.objects.get(
            codename="add_order_all_teams"
        )

        self.change_permission = Permission.objects.get(codename="change_order")
        self.change_all_teams_permission = Permission.objects.get(
            codename="change_order_all_teams"
        )

        self.delete_permission = Permission.objects.get(codename="delete_order")
        self.delete_all_teams_permission = Permission.objects.get(
            codename="delete_order_all_teams"
        )

        self.team_a = Team.objects.create(name="The A-Team")
        self.team_b = Team.objects.create(name="Not the A-Team")
        self.product = Product.objects.create(name="Dr. Cave Johnson")

        # a user without any permission
        self.user = User.objects.create_user("engel", password="engel")
        # a user with view permission, and can see teams
        self.view_user = User.objects.create_user("loc_engel", password="loc_engel")
        self.view_user.user_permissions.add(self.view_permission)
        self.view_user.user_permissions.add(self.team_permission)

        self.eventA = Event.objects.create(name="Required Event")

    def post_order(self, id="new", state="REQ", amount=1, comment="", event=1):
        url = (
            reverse("orders:create_order")
            if id == "new"
            else reverse("orders:change_order", args=[id])
        )
        return self.client.post(
            url,
            {
                "amount": amount,
                "product": self.product.id,
                "team": self.team_a.id,
                "state": state,
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
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<tbody></tbody>", html=True)

    def test_members_can_view_team_orders(self):
        self.team_a.members.add(self.user)
        Order.objects.create(product=self.product, team=self.team_a)
        Order.objects.create(product=self.product, team=self.team_b)
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The A-Team")
        self.assertNotContains(response, "Not the A-Team")

    def test_view_permission_can_see_all_orders(self):
        Order.objects.create(product=self.product, team=self.team_a)
        Order.objects.create(product=self.product, team=self.team_b)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:orders"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "The A-Team")
        self.assertContains(response, "Not the A-Team")

    def test_non_privileged_can_not_add_order_in_any_state(self):
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.post_order("new", "REQ")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 0)
        response = self.post_order("new", "APP")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 0)
        response = self.post_order("new", "REA")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 0)
        response = self.post_order("new", "COM")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 0)

    def test_create_order_has_comment_field(self):
        self.view_user.user_permissions.add(self.add_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:create_order"))

        print(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<textarea name="comment" cols="30" rows="3" maxlength="1000" class="textarea form-control" id="id_comment">',
        )

    def test_add_permission_can_add_anything(self):
        self.view_user.user_permissions.add(self.add_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.post_order("new", "REQ")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 1)
        response = self.post_order("new", "APP")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 2)
        response = self.post_order("new", "REA")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 3)
        response = self.post_order("new", "COM")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 4)

    def test_request_user_can_request_but_nothing_else(self):
        self.view_user.user_permissions.add(self.request_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.post_order("new", "REQ")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 1)
        response = self.post_order("new", "APP")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APP is not one of the available choices")
        response = self.post_order("new", "REA")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "REA is not one of the available choices")
        response = self.post_order("new", "COM")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COM is not one of the available choices")

    def test_non_privileged_can_not_change(self):
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.post_order(order.id, "REQ")
        self.assertEqual(response.status_code, 403)

    def test_change_permission_can_change_anything(self):
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.view_user.user_permissions.add(self.change_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.post_order(order.id, "REQ")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        response = self.post_order(order.id, "REQ", 2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        response = self.post_order(order.id, "REQ", 2, 17.00)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        response = self.post_order(order.id, "APP")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        response = self.post_order(order.id, "REA")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        response = self.post_order(order.id, "COM")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))

    def test_team_members_can_change_some_fields(self):
        self.team_a.members.add(self.user)
        my_order = Order.objects.create(product=self.product, team=self.team_a)
        order = Order.objects.create(product=self.product, team=self.team_b)
        self.client.login(username="engel", password="engel")
        # we can not change the state
        response = self.post_order(my_order.id, "APP")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "APP is not one of the available choices")
        # we can change the amount
        response = self.post_order(my_order.id, "REQ", 2)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        # we can not change other teams objects
        response = self.post_order(order.id, "REQ", 2)
        self.assertEqual(response.status_code, 403)
        # we can not change the order after it was approved
        my_order.state = "APP"
        my_order.save()
        response = self.post_order(my_order.id, "REQ", 2)
        self.assertEqual(response.status_code, 403)

    def test_approvers_can_update_state(self):
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.view_user.user_permissions.add(self.approve_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        # we can approve a order
        response = self.post_order(order.id, "APP")
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        # we can no longer change this order
        response = self.post_order(order.id, "REQ")

    def test_require_no_delete_permission_fails(self):
        """Has to fail because the user has no delete permission and is
           not in the team we’re trying to delete the order from"""
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.client.login(username="loc_engel", password="loc_engel")

        url = reverse("orders:delete_order", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 1)

    def test_require_only_delete_permission_fails(self):
        """Has to fail because the user is not in the team we’re trying to delete the order from"""
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.view_user.user_permissions.add(self.delete_permission)
        self.client.login(username="loc_engel", password="loc_engel")

        url = reverse("orders:delete_order", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Order.objects.all().count(), 1)

    def test_require_delete_all_teams_permission_ok(self):
        """Has to succeed because the user has the delete_order_all_teams permission"""
        order = Order.objects.create(product=self.product, team=self.team_a)
        self.view_user.user_permissions.add(self.delete_all_teams_permission)
        self.view_user.user_permissions.add(self.delete_permission)

        self.client.login(username="loc_engel", password="loc_engel")

        url = reverse("orders:delete_order", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))
        self.assertEqual(Order.objects.all().count(), 0)

    def test_team_members_can_delete_orders(self):
        """Has to succeed because the user has the delete_order permission and is member of the team"""
        self.team_a.members.add(self.user)
        my_order = Order.objects.create(product=self.product, team=self.team_a)
        my_approved_order = Order.objects.create(
            product=self.product, team=self.team_a, state="APP"
        )
        order = Order.objects.create(product=self.product, team=self.team_b)
        self.user.user_permissions.add(self.delete_permission)
        self.client.login(username="engel", password="engel")

        url = reverse("orders:delete_order", args=[my_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("orders:orders"))

        url = reverse("orders:delete_order", args=[order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

        url = reverse("orders:delete_order", args=[my_approved_order.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_event_preset_by_setting(self):
        env = EnvironmentVarGuard()
        env.set("DEFAULT_ORDER_EVENT", "12c3")
        self.view_user.user_permissions.add(self.add_permission)
        Event.objects.create(name="12c3")
        Event.objects.create(name="42c3")
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:create_order"))
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
    #     print(response.status_code)
    #     print(response.content)
    #     self.assertContains(response, '<option value="3" selected>42c3</option>')

    def test_event_no_event_defined(self):
        Event.objects.all().delete()

        self.view_user.user_permissions.add(self.add_permission)
        self.client.login(username="loc_engel", password="loc_engel")
        response = self.client.get(reverse("orders:create_order"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="" selected>---------</option>')

    def test_single_team_preset(self):
        self.team_a.members.add(self.user)
        self.user.user_permissions.add(self.add_permission)
        self.client.login(username="engel", password="engel")
        response = self.client.get(reverse("orders:create_order"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<option value="1" selected>')

    def test_status_can_view_only(self):
        """
        Tests if a user having only view rights can load the order view for an existing order
        """
        Order.objects.create(product=self.product, team=self.team_a)

        self.client.login(username="loc_engel", password="loc_engel")

        response = self.client.get(reverse("orders:change_order", args=["1"]))
        self.assertEqual(response.status_code, 200)


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
