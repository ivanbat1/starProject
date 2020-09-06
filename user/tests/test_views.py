import json
import jwt
from django.test import TestCase

# Create your tests here.
from user.models import Users
from starProject.settings import SECRET_KEY


class UsersRegistrationAPITest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        resp = self.client.post('/api/v1/user/registration/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_with_true_registration_data(self):
        true_data = {'username': 'ivan', 'password1': 'test', 'password2': 'test', 'email': 'test@gmail.com'}
        resp = self.client.post('/api/v1/user/registration/', data=true_data)
        content = json.loads(resp.content)
        token = content.get('token')
        body = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = Users.objects.get(id=body.get('user_id'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(user)
        self.assertEqual(user.username, true_data.get('username'))
        self.assertEqual(user.password, true_data.get('password1'))
        self.assertEqual(user.email, true_data.get('email'))

    def test_view_url_with_false_registration_password(self):
        false_data = {'username': 'ivan', 'password1': 'test', 'password2': 'te23423st'}
        resp = self.client.post('/api/v1/user/registration/', data=false_data)
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(content.get('error'), 'password don\'t match')

    def test_view_url_with_false_registration_username(self):
        false_data = {'username': '', 'password1': 'test', 'password2': 'test'}
        resp = self.client.post('/api/v1/user/registration/', data=false_data)
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(content.get('error'), 'username exist')

    def test_view_url_with_false_registration_data(self):
        false_data = {'username': '', 'password1': 'tew34fst', 'password2': 'test'}
        resp = self.client.post('/api/v1/user/registration/', data=false_data)
        content = json.loads(resp.content)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(content.get('error'), 'username exist')


class UsersLoginAPITest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.true_data = {'username': 'ivan', 'password1': 'test', 'password2': 'test', 'email': 'test@gmail.com'}

    def setUp(self):
        self.client.post('/api/v1/user/registration/', data=self.true_data)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/api/v1/user/login/')
        self.assertEqual(resp.status_code, 401)

    def test_view_url_with_true_login_data(self):
        str_login = '"username": "{username}", "password": "{password}"'.format(
            username=self.true_data.get('username'),
            password=self.true_data.get('password1')
        )
        resp = self.client.get('/api/v1/user/login/?auth={' + str_login + '}')
        content = json.loads(resp.content)
        token = content.get('token')
        body = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = Users.objects.get(id=body.get('user_id'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(token)
        self.assertEqual(user.username, self.true_data.get('username'))
        self.assertEqual(user.password, self.true_data.get('password1'))

    def test_view_url_with_false_login_data(self):
        str_login = '"username": "{username}", "password": "{password}"'.format(
            username=self.true_data.get('username') + 'blablabla',
            password=self.true_data.get('password1')
        )
        resp = self.client.get('/api/v1/user/login/?auth={' + str_login + '}')
        self.assertEqual(resp.status_code, 401)

    def test_view_url_with_false_login_password(self):
        str_login = '"username": "{username}", "password": "{password}"'.format(
            username=self.true_data.get('username'),
            password=self.true_data.get('password1') + '1231'
        )
        resp = self.client.get('/api/v1/user/login/?auth={' + str_login + '}')
        self.assertEqual(resp.status_code, 401)
