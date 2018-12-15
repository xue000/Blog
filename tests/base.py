import unittest

from flask import url_for

from blog import create_app
from blog.extensions import db
from blog.models import User, Role, Post, Comment, Category


class BaseTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        self.context = app.test_request_context()
        self.context.push()
        self.client = app.test_client()
        self.runner = app.test_cli_runner()

        db.create_all()
        Role.init_role()

        admin_user = User(email='admin@helloflask.com', name='Admin', username='admin')
        admin_user.set_password('123')
        admin_user.set_role()
        normal_user = User(email='normal@helloflask.com', name='Normal User', username='normal')
        normal_user.set_password('123')
        unconfirmed_user = User(email='unconfirmed@helloflask.com', name='Unconfirmed', username='unconfirmed',
                                )
        unconfirmed_user.set_password('123')
        locked_user = User(email='locked@helloflask.com', name='Locked User', username='locked',
                            locked=True)
        locked_user.set_password('123')
        locked_user.lock()

        blocked_user = User(email='blocked@helloflask.com', name='Blocked User', username='blocked',
                             active=False)
        blocked_user.set_password('123')




        category = Category(name='test category')
        post = Post(title='test post', body='Test post', category=category)
        comment = Comment(body='test comment body', post=post, author=normal_user)
        db.session.add_all([admin_user, normal_user, unconfirmed_user, locked_user, blocked_user])
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.context.pop()

    def login(self, email=None, password=None):
        if email is None and password is None:
            email = 'normal@helloflask.com'
            password = '123'

        return self.client.post(url_for('auth.login'), data=dict(
            email=email,
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.client.get(url_for('auth.logout'), follow_redirects=True)
