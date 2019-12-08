from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordChangeForm, PasswordResetForm
from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import resolve, reverse


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


class PasswordChangeTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="any_user", password="uiafge489w9834sronuisw"
        )
        self.client.login(username="any_user", password="uiafge489w9834sronuisw")

        url = reverse("password_change")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/change")
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self):
        self.assertContains(self.response, "csrfmiddlewaretoken")

    def test_contains_form(self):
        print(repr(self.response))
        form = self.response.context.get("form")
        self.assertIsInstance(form, PasswordChangeForm)

    def test_form_inputs(self):
        """The view must contain five inputs: csrf, old password, 2 * new password and the button"""
        self.assertContains(self.response, "<input", 5)
        self.assertContains(self.response, 'type="password"', 3)


class SuccessfulPasswordChangeTests(TestCase):
    def setUp(self):
        email = "test@example.com"
        User.objects.create_user(
            username="test", email=email, password="ufgdlneginetriunae"
        )
        url = reverse("password_change")
        self.response = self.client.post(url, {"email": email})


class PasswordChangeDoneTests(TestCase):
    def setUp(self):
        url = reverse("password_change_done")
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 302)

    def test_view_function(self):
        view = resolve("/change/done")
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeDoneView)
