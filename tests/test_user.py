# from flask import url_for
#
# from blog.models import User

# from tests.base import BaseTestCase
# class UserTestCase(BaseTestCase):
#     def test_edit_profile(self):
#         self.login()
#         response = self.client.post(url_for('user.edit_profile'), data=dict(
#             username='newname',
#             name='New Name',
#         ), follow_redirects=True)
#         data = response.get_data(as_text=True)
#         self.assertIn('Profile updated.', data)
#         user = User.query.get(2)
#         self.assertEqual(user.name, 'New Name')
#         self.assertEqual(user.username, 'newname')
#
#     def test_change_password(self):
#         user = User.query.get(2)
#         self.assertTrue(user.validate_password('123'))
#
#         self.login()
#         response = self.client.post(url_for('user.change_password'), data=dict(
#             old_password='123',
#             password='new-password',
#             password2='new-password',
#         ), follow_redirects=True)
#         data = response.get_data(as_text=True)
#         self.assertIn('Password updated.', data)
#         self.assertTrue(user.validate_password('new-password'))
#         self.assertFalse(user.validate_password('old-password'))