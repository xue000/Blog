from flask import render_template, Blueprint, request, flash, redirect, url_for, current_app, abort
from blog.extensions import db
from blog.models import User, Post, Comment, Category
from flask_login import current_user, login_required
from blog.forms.auth import AdminCommentForm, CommentForm, PostForm
from blog.utils import redirect_back
from blog.decorators import permission_required
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = current_app.config['BLOG_POST_PER_PAGE']
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page, per_page=per_page)
    posts = pagination.items
    categories = Category.query.all()
    return render_template('main/index.html', pagination=pagination, posts=posts, categories=categories)


@main_bp.route('/category/<int:category_id>')
def show_category(category_id):
    category = Category.query.get_or_404(category_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Post.query.with_parent(category).order_by(Post.timestamp.desc()).paginate(page, per_page)
    posts = pagination.items
    return render_template('main/category.html', category=category, pagination=pagination, posts=posts)


@main_bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def show_post(post_id):
    categories = Category.query.all()
    post = Post.query.get_or_404(post_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Comment.query.with_parent(post).order_by(Comment.timestamp.asc()).paginate(
        page, per_page)
    comments = pagination.items

    # if current_user.is_authenticated:
    #     form = AdminCommentForm()
    #     form.author.data = current_user.name
    #     # form.email.data = current_app.config['BLUELOG_EMAIL']
    #     form.site.data = url_for('.index')
    #     from_admin = True
    # else:
    form = CommentForm()


    if form.validate_on_submit():
        body = form.body.data
        comment = Comment(
            author=current_user, body=body, post=post)
        replied_id = request.args.get('reply')
        if replied_id:
            replied_comment = Comment.query.get_or_404(replied_id)
            comment.replied = replied_comment
        db.session.add(comment)
        db.session.commit()
        flash('Comment published.', 'success')
        return redirect(url_for('.show_post', post_id=post_id))
    return render_template('main/post.html', post=post, pagination=pagination, form=form, comments=comments, categories=categories)

@main_bp.route('/post/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    form = PostForm()
    post = Post.query.get_or_404(post_id)
    if current_user != post.author and not current_user.can('MODERATE'):
        abort(403)
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        post.category = Category.query.get(form.category.data)
        db.session.commit()
        flash('Post updated.', 'success')
        return redirect(url_for('main.show_post', post_id=post.id))
    form.title.data = post.title
    form.body.data = post.body
    form.category.data = post.category_id
    return render_template('admin/edit_post.html', form=form)

@main_bp.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user != post.author and not current_user.can('MODERATE'):
        abort(403)

    db.session.delete(post)
    db.session.commit()
    flash('Post deleted.', 'success')
    return redirect_back()

@main_bp.route('/comment/<int:comment_id>/delete', methods=['POST'])
@permission_required('MODERATE')
@login_required
def delete_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash('Comment deleted.', 'success')
    return redirect_back()

@main_bp.route('/post/<int:post_id>/set-comment', methods=['POST'])
@permission_required('MODERATE')
@login_required
def set_comment(post_id):
    post = Post.query.get_or_404(post_id)
    if post.can_comment:
        post.can_comment = False
        flash('Comment disabled.', 'success')
    else:
        post.can_comment = True
        flash('Comment enabled.', 'success')
    db.session.commit()
    return redirect_back()

@main_bp.route('/reply/comment/<int:comment_id>')
@permission_required('COMMENT')
def reply_comment(comment_id):
    comment = Comment.query.get_or_404(comment_id)
    if not comment.post.can_comment:
        flash('Comment is disabled.', 'warning')
        return redirect(url_for('.show_post', post_id=comment.post.id))
    return redirect(
        url_for('.show_post', post_id=comment.post_id, reply=comment_id, author=comment.author) + '#comment-form')

# @main_bp.route('/search')
# def search():
#     q = request.args.get('q', '')
#     if q == '':
#         flash('Enter keyword about post.', 'warning')
#         return redirect_back()
#
#     category = request.args.get('category', 'post')
#     page = request.args.get('page', 1, type=int)
#     per_page = current_app.config['BLOG_SEARCH_RESULT_PER_PAGE']
#     if category == 'post':
#         pagination = Post.query.whooshee_search(q).paginate(page, per_page)
#     # elif category == 'user':
#     #     pagination = User.query.whooshee_search(q).paginate(page, per_page)
#     elif category == 'comment':
#         pagination = Comment.query.whooshee_search(q).paginate(page, per_page)
#     results = pagination.items
#     return render_template('main/search.html', q=q, results=results, pagination=pagination, category=category)
