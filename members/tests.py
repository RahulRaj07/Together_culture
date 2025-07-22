from django.test import TestCase, Client
from django.urls import reverse
from members.models import Member, Interest
from django.contrib.auth.models import AnonymousUser
from django.core import mail
from unittest.mock import patch


class MemberViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Create interests
        self.interest = Interest.objects.create(name="Caring")

        # Create regular user (unapproved)
        self.user = Member.objects.create_user(
            username="user1", email="user1@test.com", password="pass1234",
            is_admin=False, is_approved=False
        )
        self.user.interests.add(self.interest)

        # Create approved user
        self.approved_user = Member.objects.create_user(
            username="user2", email="user2@test.com", password="pass1234",
            is_admin=False, is_approved=True
        )

        # Create admin user
        self.admin = Member.objects.create_user(
            username="admin", email="admin@test.com", password="admin123",
            is_admin=True, is_approved=True
        )

    def test_homepage(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_apply_membership_get(self):
        response = self.client.get(reverse('apply'))
        self.assertEqual(response.status_code, 200)

    def test_apply_membership_post(self):
        response = self.client.post(reverse('apply'), {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@app.com",
            "phone_number": "1234567890",
            "location": "TestCity",
            "interests": [self.interest.id],
            "professional_background": "Tester",
            "why_join": "Testing purpose",
            "how_contribute": "Test contribution",
            "agree_terms": True,
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('application_success'))

    def test_application_success_view(self):
        response = self.client.get(reverse('application_success'))
        self.assertEqual(response.status_code, 200)

    def test_login_user_invalid(self):
        response = self.client.post(reverse('login'), {
            "username": "fake@test.com",
            "password": "wrong"
        })
        self.assertContains(response, "Please enter a correct username and password")

    def test_login_user_approved(self):
        logged_in = self.client.login(username=self.approved_user.username, password='pass1234')
        self.assertTrue(logged_in)
        response = self.client.post(reverse('login'), {
            "username": self.approved_user.username,
            "password": "pass1234"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_login_user_unapproved(self):
        logged_in = self.client.login(username=self.user.username, password='pass1234')
        self.assertTrue(logged_in)
        response = self.client.post(reverse('login'), {
            "username": self.user.username,
            "password": "pass1234"
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('user_dashboard'))

    def test_admin_home_get(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('admin_home'))
        self.assertEqual(response.status_code, 200)

    @patch("members.views.send_mail")
    def test_approve_member_and_email_sent(self, mock_send):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('approve_member', args=[self.user.id]))
        self.assertEqual(response.status_code, 302)
        mock_send.assert_called_once()

    def test_member_details_valid(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('member_details', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("email", response.json())

    def test_member_details_invalid(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('member_details', args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_user_dashboard_regular(self):
        self.client.login(username='user2', password='pass1234')
        response = self.client.get(reverse('user_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_user_dashboard_admin_redirect(self):
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('user_dashboard'))
        self.assertRedirects(response, reverse('admin_home'))
