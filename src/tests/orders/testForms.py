from django.contrib.auth.models import Permission, User
from django.test import TestCase
from squirrel.orders.forms import OrderForm
from squirrel.orders.models import Event, Product, Team


class ProductFormTests(TestCase):
    pass


class OrderFormTests(TestCase):
    def setUp(self) -> None:
        User.objects.create_user(username="not_team_member", password="test123")

        self.teamA = Team.objects.create(name="A team where the name starts with A")

        self.user = User.objects.create_user(username="team_member", password="test123")
        self.teamB = Team.objects.create(name="Bottles")
        self.teamB.members.add(self.user)
        self.teamB.save()

        self.teamZ = Team.objects.create(name="Zebus are a team now, too.")

        helpdesk = User.objects.create_user(username="helpdesk", password="test123")
        helpdesk.user_permissions.add(Permission.objects.get(codename="view_team"))
        helpdesk.user_permissions.add(Permission.objects.get(codename="add_order"))

        self.productB = Product.objects.create(name="Tardis")

        self.productA = Product.objects.create(name="Apple")
        self.productZ = Product.objects.create(name="Zotz")

        self.eventA = Event.objects.create(name="36C3")
        self.eventB = Event.objects.create(name="Another event")
        self.eventC = Event.objects.create(name="Test Event 3")

    def test_sorted_teams(self):
        """Teams are sorted alphabetically"""
        form = OrderForm(teams=Team.objects.all())

        self.assertEqual(form.fields["team"].queryset[0], self.teamA)
        self.assertEqual(form.fields["team"].queryset[1], self.teamB)
        self.assertEqual(form.fields["team"].queryset[2], self.teamZ)
        self.assertEqual(len(form.fields["team"].queryset), 3)

    def test_sorted_events(self):
        """Events are sorted by id"""
        form = OrderForm(teams=Team.objects.all())

        self.assertEqual(form.fields["event"].queryset[0], self.eventC)
        self.assertEqual(form.fields["event"].queryset[1], self.eventB)
        self.assertEqual(form.fields["event"].queryset[2], self.eventA)
        self.assertEqual(len(form.fields["event"].queryset), 3)

    def test_sorted_products(self):
        """Products are sorted alphabetically"""
        form = OrderForm(teams=Team.objects.all())

        self.assertEqual(form.fields["product"].queryset[0], self.productA)
        self.assertEqual(form.fields["product"].queryset[1], self.productB)
        self.assertEqual(form.fields["product"].queryset[2], self.productZ)
        self.assertEqual(len(form.fields["product"].queryset), 3)

    def test_require_amount(self):
        form_data = {
            "product": self.productB.name,
            "team": self.teamB.id,
            "event": self.eventA,
        }
        form = OrderForm(data=form_data, teams=Team.objects.all())
        self.assertFalse(form.is_valid())
        form_data["amount"] = 1
        form = OrderForm(data=form_data, teams=Team.objects.all())
        self.assertTrue(form.is_valid())
