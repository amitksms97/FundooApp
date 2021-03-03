from django.test import TestCase
from ..models import User


class RegistrationTest(TestCase):
    """ Test module for Registration model """

    def setUp(self):
        User.objects.create(
            username='amitksms97', email='amitksms97@gmail.com', password1='amit123', password2='amit123'
        )
        User.objects.create(
            username='admin', email='admin@gmail.com', password1='admin123', password2='admin123'
        )

    def test_registeration_username(self):
        registration_amit = User.objects.get(username='amitksms97')
        registration_admin = User.objects.get(username='admin')
        self.assertEqual(registration_amit.get_username(), "amit")
        self.assertEqual(registration_admin.get_username(), "admin")

    def test_registeration_email(self):
        registration_amit_email = User.objects.get(username='amitksms97')
        registration_admin_email = User.objects.get(username='admin')
        self.assertEqual(registration_amit_email.get_email(), "amitksms97@gmail.com")
        self.assertEqual(registration_admin_email.get_email(), "admin@gmail.com")
