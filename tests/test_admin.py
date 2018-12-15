from flask import url_for

from blog.extensions import db
from blog.models import User, Role, Category, Post
from tests.base import BaseTestCase
#
#
class AdminTestCase(BaseTestCase):
    def setUp(self):
        super(AdminTestCase, self).setUp()
        self.login(email='admin@helloflask.com', password='123')

    def test_index_page(self):
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertIn('Blog Dashboard', data)

    def test_bad_permission(self):
        self.logout()
        response = self.client.get(url_for('admin.index'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Please log in to access this page', data)
        self.assertNotIn('Blog Dashboard', data)

        self.login()  # normal user, without MODERATOR permission
        response = self.client.get(url_for('admin.index'))
        data = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('Blog Dashboard', data)

    def test_edit_profile_admin(self):
        role_id = Role.query.filter_by(name='Locked').first().id
        response = self.client.post(url_for('admin.edit_profile_admin', user_id=2), data=dict(
            username='newname',
            role=role_id,
            confirmed=True,
            active=True,
            name='New Name',
            email='new@helloflask.com'
        ), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Profile updated.', data)
        user = User.query.get(2)
        self.assertEqual(user.name, 'New Name')
        self.assertEqual(user.username, 'newname')
        self.assertEqual(user.email, 'new@helloflask.com')
        self.assertEqual(user.role.name, 'Locked')

    def test_block_user(self):
        response = self.client.post(url_for('admin.block_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Account blocked.', data)
        user = User.query.get(2)
        self.assertEqual(user.active, False)

    def test_unblock_user(self):
        user = User.query.get(2)
        user.active = False
        db.session.commit()
        self.assertEqual(user.active, False)

        response = self.client.post(url_for('admin.unblock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Block canceled.', data)
        user = User.query.get(2)
        self.assertEqual(user.active, True)

    def test_lock_user(self):
        response = self.client.post(url_for('admin.lock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Account locked.', data)
        user = User.query.get(2)
        self.assertEqual(user.role.name, 'Locked')

    def test_unlock_user(self):
        user = User.query.get(2)
        user.role = Role.query.filter_by(name='Locked').first()
        db.session.commit()
        self.assertEqual(user.role.name, 'Locked')

        response = self.client.post(url_for('admin.unlock_user', user_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Lock canceled.', data)
        user = User.query.get(2)
        self.assertEqual(user.role.name, 'User')

    def test_delete_category(self):
        category = Category(name='Tech')
        post = Post(title='test', category=category)
        db.session.add(category)
        db.session.add(post)
        db.session.commit()
        self.assertIsNotNone(category.query.get(1))

        # response = self.client.get(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        # data = response.get_data(as_text=True)
        # self.assertNotIn('Category deleted.', data)
        # self.assertIn('405 Method Not Allowed', data)

        response = self.client.post(url_for('admin.delete_category', category_id=1), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('You can not delete the default category.', data)
        self.assertNotIn('Category deleted.', data)
        # self.assertIn('Default', data)

        response = self.client.post(url_for('admin.delete_category', category_id=2), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Category deleted.', data)
        # self.assertIn('Default', data)
        self.assertNotIn('Tech', data)

    def test_manage_user_page(self):
        response = self.client.get(url_for('admin.manage_user'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertIn('Locked', data)
        self.assertIn('Normal', data)

        response = self.client.get(url_for('admin.manage_user', filter='locked'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='blocked'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='administrator'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertNotIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

        response = self.client.get(url_for('admin.manage_user', filter='moderator'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Users', data)
        self.assertIn('Admin', data)
        self.assertNotIn('Blocked User', data)
        self.assertNotIn('Locked User', data)
        self.assertNotIn('Normal User', data)

    def test_manage_post_page(self):
        response = self.client.get(url_for('admin.manage_post'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Posts', data)
        # self.assertIn('Order by flag <span class="oi oi-elevator"></span>', data)

        response = self.client.get(url_for('admin.manage_post'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Posts', data)

    def test_manage_category_page(self):
        response = self.client.get(url_for('admin.manage_category'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Categories', data)

    def test_manage_comment_page(self):
        response = self.client.get(url_for('admin.manage_comment'))
        data = response.get_data(as_text=True)
        self.assertIn('Manage Comments', data)
#     def setUp(self):
#         super(AdminTestCase, self).setUp()
#         self.login(email='admin@helloflask.com', password='helloflask')
#
#     def test_index_page(self):
#         response = self.client.get(url_for('admin.index'))
#         data = response.get_data(as_text=True)
#         self.assertIn('Blog Dashboard', data)
#
#     # def test_bad_permission(self):
#     #     self.logout()
#     #     response = self.client.get(url_for('admin.index'), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Please log in to access this page.', data)
#     #     self.assertNotIn('Blog Dashboard', data)
#     #
#     #     self.login()  # normal user, without MODERATOR permission
#     #     response = self.client.get(url_for('admin.index'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertEqual(response.status_code, 403)
#     #     self.assertNotIn('Blog Dashboard', data)
#
#     # def test_edit_profile_admin(self):
#     #     role_id = Role.query.filter_by(name='Locked').first().id
#     #     response = self.client.post(url_for('admin.edit_profile_admin', user_id=2), data=dict(
#     #         username='newname',
#     #         role=role_id,
#     #         confirmed=True,
#     #         active=True,
#     #         name='New Name',
#     #         email='new@helloflask.com'
#     #     ), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Profile updated.', data)
#     #     user = User.query.get(2)
#     #     self.assertEqual(user.name, 'New Name')
#     #     self.assertEqual(user.username, 'newname')
#     #     self.assertEqual(user.email, 'new@helloflask.com')
#     #     self.assertEqual(user.role.name, 'Locked')
#     #
#     # def test_block_user(self):
#     #     response = self.client.post(url_for('admin.block_user', user_id=2), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Account blocked.', data)
#     #     user = User.query.get(2)
#     #     self.assertEqual(user.active, False)
#
#     # def test_unblock_user(self):
#     #     user = User.query.get(2)
#     #     user.active = False
#     #     db.session.commit()
#     #     self.assertEqual(user.active, False)
#     #
#     #     response = self.client.post(url_for('admin.unblock_user', user_id=2), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Block canceled.', data)
#     #     user = User.query.get(2)
#     #     self.assertEqual(user.active, True)
#     #
#     # def test_lock_user(self):
#     #     response = self.client.post(url_for('admin.lock_user', user_id=2), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Account locked.', data)
#     #     user = User.query.get(2)
#     #     self.assertEqual(user.role.name, 'Locked')
#     #
#     # def test_unlock_user(self):
#     #     user = User.query.get(2)
#     #     user.role = Role.query.filter_by(name='Locked').first()
#     #     db.session.commit()
#     #     self.assertEqual(user.role.name, 'Locked')
#     #
#     #     response = self.client.post(url_for('admin.unlock_user', user_id=2), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Lock canceled.', data)
#     #     user = User.query.get(2)
#     #     self.assertEqual(user.role.name, 'User')
#     #
#     # def test_delete_category(self):
#     #     category = Category()
#     #     db.session.add(category)
#     #     db.session.commit()
#     #     self.assertIsNotNone(Category.query.get(1))
#     #
#     #     response = self.client.post(url_for('admin.delete_category', tag_id=1), follow_redirects=True)
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Category deleted.', data)
#     #     self.assertEqual(Category.query.get(1), None)
#
#     # def test_manage_user_page(self):
#     #     response = self.client.get(url_for('admin.manage_user'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Users', data)
#     #     self.assertIn('Admin', data)
#     #     self.assertIn('Locked', data)
#     #     self.assertIn('Normal', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_user', filter='locked'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Users', data)
#     #     self.assertIn('Locked User', data)
#     #     self.assertNotIn('Normal User', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_user', filter='blocked'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Users', data)
#     #     self.assertIn('Blocked User', data)
#     #     self.assertNotIn('Locked User', data)
#     #     self.assertNotIn('Normal User', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_user', filter='administrator'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Users', data)
#     #     self.assertIn('Admin', data)
#     #     self.assertNotIn('Blocked User', data)
#     #     self.assertNotIn('Locked User', data)
#     #     self.assertNotIn('Normal User', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_user', filter='moderator'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Users', data)
#     #     self.assertIn('Admin', data)
#     #     self.assertNotIn('Blocked User', data)
#     #     self.assertNotIn('Locked User', data)
#     #     self.assertNotIn('Normal User', data)
#     #
#     # def test_manage_post_page(self):
#     #     response = self.client.get(url_for('admin.manage_post'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Posts', data)
#     #     self.assertIn('Order by flag <span class="oi oi-elevator"></span>', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_post', order='by_time'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Posts', data)
#     #     self.assertIn('Order by time <span class="oi oi-elevator"></span>', data)
#     #
#     # def test_manage_category_page(self):
#     #     response = self.client.get(url_for('admin.manage_category'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Categoriess', data)
#     #
#     # def test_manage_comment_page(self):
#     #     response = self.client.get(url_for('admin.manage_comment'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Comments', data)
#     #     self.assertIn('Order by flag <span class="oi oi-elevator"></span>', data)
#     #
#     #     response = self.client.get(url_for('admin.manage_comment', order='by_time'))
#     #     data = response.get_data(as_text=True)
#     #     self.assertIn('Manage Comments', data)
#     #     self.assertIn('Order by time <span class="oi oi-elevator"></span>', data)
