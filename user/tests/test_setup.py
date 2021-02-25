from rest_framework.test import APITestCase
from django.urls import reverse
from faker import Faker
import pdb
# Create your tests here.


class TestSetUp(APITestCase):

    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.fake = Faker()

        self.user_data = {
            'email': self.fake.email(),
            'username': self.fake.email().split('@')[0],
            'password': self.fake.email().split('@')[0],
            #'email': "email@gmail.com",
            #'username': "email",
            #'password': "email@gmsil.com"
        }
        #pdb.set_trace()

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


