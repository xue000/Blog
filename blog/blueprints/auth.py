from flask import render_template, flash, redirect, url_for, Blueprint
from flask_login import login_user, logout_user, login_required, current_user, login_fresh, confirm_login

# from blog.emails import send_confirm_email, send_reset_password_email
from blog.extensions import db
from blog.forms.auth import LoginForm, RegisterForm, ForgetPasswordForm, ResetPasswordForm, PostForm
from blog.models import User, Category, Post
# from blog.settings import Operations
from blog.utils import redirect_back
# from blog.utils import generate_token, validate_token
auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.validate_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash('Login success.', 'info')
            return redirect_back()
        flash('Invalid email or password.', 'warning')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout success.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data.lower()
        username = form.username.data
        password = form.password.data
        user = User(name=name, email=email, username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        # token = generate_token(user=user, operation='confirm')
        # send_confirm_email(user=user, token=token)
        flash('Register successfully.', 'info')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)


# @auth_bp.route('/confirm/<token>')
# @login_required
# def confirm(token):
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#
#     if validate_token(user=current_user, token=token, operation=Operations.CONFIRM):
#         flash('Account confirmed.', 'success')
#         return redirect(url_for('main.index'))
#     else:
#         flash('Invalid or expired token.', 'danger')
#         return redirect(url_for('.resend_confirm_email'))
#
#
# @auth_bp.route('/resend-confirm-email')
# @login_required
# def resend_confirm_email():
#     if current_user.confirmed:
#         return redirect(url_for('main.index'))
#
#     token = generate_token(user=current_user, operation=Operations.CONFIRM)
#     send_confirm_email(user=current_user, token=token)
#     flash('New email sent, check your inbox.', 'info')
#     return redirect(url_for('main.index'))
#
#
# @auth_bp.route('/forget-password', methods=['GET', 'POST'])
# def forget_password():
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#
#     form = ForgetPasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data.lower()).first()
#         if user:
#             token = generate_token(user=user, operation=Operations.RESET_PASSWORD)
#             send_reset_password_email(user=user, token=token)
#             flash('Password reset email sent, check your inbox.', 'info')
#             return redirect(url_for('.login'))
#         flash('Invalid email.', 'warning')
#         return redirect(url_for('.forget_password'))
#     return render_template('auth/reset_password.html', form=form)

#
# @auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
# def reset_password(token):
#     if current_user.is_authenticated:
#         return redirect(url_for('main.index'))
#
#     form = ResetPasswordForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(email=form.email.data.lower()).first()
#         if user is None:
#             return redirect(url_for('main.index'))
#         if validate_token(user=user, token=token, operation=Operations.RESET_PASSWORD,
#                           new_password=form.password.data):
#             flash('Password updated.', 'success')
#             return redirect(url_for('.login'))
#         else:
#             flash('Invalid or expired link.', 'danger')
#             return redirect(url_for('.forget_password'))
#     return render_template('auth/reset_password.html', form=form)

@auth_bp.route('/post/new', methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        title = form.title.data
        body = form.body.data
        category = Category.query.get(form.category.data)
        post = Post(title=title, body=body, category=category)
        db.session.add(post)
        db.session.commit()
        flash('Post created.', 'success')
        return redirect(url_for('show_post', post_id=post.id))
    return render_template('new_post.html', form=form)

