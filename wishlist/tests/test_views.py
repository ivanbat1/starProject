import json
import jwt
from django.test import TestCase

# Create your tests here.
from user.models import Users
from starProject.settings import SECRET_KEY
from wishlist.models import WishLists


class WishListAPITest(TestCase):
    def setUp(self):
        true_data = {'username': 'ivan', 'password1': 'test', 'password2': 'test', 'email': 'test@gmail.com'}
        resp = self.client.post('/api/v1/user/registration/', data=true_data)
        content = json.loads(resp.content)
        self.token = content.get('token')
        self.extra = {
            'HTTP_AUTHORIZATION': "Bearer JWT " + self.token
        }
        body = jwt.decode(self.token, SECRET_KEY, algorithms=['HS256'])
        self.user = Users.objects.get(id=body.get('user_id'))
        self.token_body = jwt.decode(self.token, SECRET_KEY, algorithms=['HS256'])

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/api/v1/wishlist/', **self.extra)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/api/v1/wishlist/')
        self.assertEqual(resp.status_code, 401)

    def test_view_url_create_wishlist_with_true_data(self):
        create_data = {'title': 'title', 'text': 'text'}
        resp = self.client.post('/api/v1/wishlist/create/', data=create_data, **self.extra)
        content = json.loads(resp.content)
        wishlist = content.get('message')
        wish_db = WishLists.objects.get(id=wishlist.get('id'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(wish_db)
        self.assertEqual(wishlist.get('author_id'), self.user.id)
        self.assertEqual(wishlist.get('author_id'), wish_db.author.id)
        self.assertEqual(wishlist.get('title'), create_data.get('title'))
        self.assertEqual(wishlist.get('title'), wish_db.title)
        self.assertEqual(wishlist.get('text'), create_data.get('text'))
        self.assertEqual(wishlist.get('text'), wish_db.text)

    def test_view_url_create_wishlist_with_items(self):
        create_data = {'title': 'title', 'text': 'text', 'items': "[{'text': 'item_text'}, {'text': 'item2_text'}]"}
        resp = self.client.post('/api/v1/wishlist/create/', data=create_data, **self.extra)
        content = json.loads(resp.content)
        message = content.get('errors')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(message)

    def test_view_url_create_wishlist_with_false_data(self):
        create_data = {'text': 'text'}
        resp = self.client.post('/api/v1/wishlist/create/', data=create_data, **self.extra)
        content = json.loads(resp.content)
        message = content.get('errors')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(message)


class WishAPITest(TestCase):
    def setUp(self):
        true_data = {'username': 'ivan', 'password1': 'test', 'password2': 'test', 'email': 'test@gmail.com'}
        resp = self.client.post('/api/v1/user/registration/', data=true_data)
        content = json.loads(resp.content)
        self.token = content.get('token')
        self.extra = {
            'HTTP_AUTHORIZATION': "Bearer JWT " + self.token
        }
        body = jwt.decode(self.token, SECRET_KEY, algorithms=['HS256'])
        self.user = Users.objects.get(id=body.get('user_id'))
        self.token_body = jwt.decode(self.token, SECRET_KEY, algorithms=['HS256'])
        create_data = {'title': 'title', 'text': 'text'}
        self.client.post('/api/v1/wishlist/create/', data=create_data, **self.extra)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/api/v1/wishlist/1/', **self.extra)
        content = json.loads(resp.content)
        wish = content.get('message')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(wish)
        self.assertEqual(wish.get('id'), 1)

    def test_view_url_update_wish_with_true_data(self):
        update_data = {'title': 'title_update', 'text': 'text_update'}
        wish = WishLists.objects.filter(author_id=self.user.id).first()
        resp = self.client.put('/api/v1/wishlist/{}/'.format(wish.id),
                               data=update_data,
                               content_type='application/json',
                               **self.extra)
        content = json.loads(resp.content)
        wish_update = content.get('message')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(wish)
        self.assertEqual(wish_update.get('id'), wish.id)
        self.assertEqual(wish_update.get('title'), update_data.get('title'))
        self.assertEqual(wish_update.get('text'), update_data.get('text'))

    def test_view_url_update_wish_with_false_data(self):
        update_data = {'text': 'text_update'}
        wish = WishLists.objects.filter(author_id=self.user.id).first()
        resp = self.client.put('/api/v1/wishlist/{}/'.format(wish.id),
                               data=update_data,
                               content_type='application/json',
                               **self.extra)
        content = json.loads(resp.content)
        errors = content.get('errors')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(errors)

    def test_view_url_update_wish_with_false_id(self):
        update_data = {'text': 'text_update'}
        req_data = {'path': '/api/v1/wishlist/10000/',
                    'data': update_data,
                    'content_type': 'application/json'}
        resp_put = self.client.put(**req_data, **self.extra)
        resp_del = self.client.delete(**req_data, **self.extra)
        resp_get = self.client.get(**req_data, **self.extra)
        self.assertEqual(resp_put.status_code, 200)
        self.assertEqual(resp_del.status_code, 200)
        self.assertEqual(resp_get.status_code, 200)
        for resp in [resp_put, resp_del, resp_get]:
            content = json.loads(resp.content)
            message = content.get('message')
            self.assertTrue(message)
            self.assertEqual(message, 'wishlist does not exist')

    def test_view_url_delete_wish(self):
        wish = WishLists.objects.filter(author_id=self.user.id).first()
        resp = self.client.delete('/api/v1/wishlist/{}/'.format(wish.id),
                                  content_type='application/json',
                                  **self.extra)
        content = json.loads(resp.content)
        message = content.get('message')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(message)
        self.assertEqual(message, 'wishlist delete')

