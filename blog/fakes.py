import random
from faker import Faker
from sqlalchemy.exc import IntegrityError

from blog.extensions import db
from blog.models import User, Category, Comment, Post

fake = Faker()


def fake_admin():
    admin = User(name='Difan Xue',
                 username='xuedifan',
                 email='admin@helloflask.com',
                 bio=fake.sentence(),
                 location=fake.city(),
                 member_since=fake.date_this_decade(),
                 website='http://xuedifan.pythonanywhere.com',
                 )
    admin.set_password('helloflask')
    db.session.add(admin)
    db.session.commit()


def fake_user(count=10):
    for i in range(count):
        user = User(name=fake.name(),
                    username=fake.user_name(),
                    bio=fake.sentence(),
                    location=fake.city(),
                    website=fake.url(),
                    member_since=fake.date_this_decade(),
                    email=fake.email())
        user.set_password('123456')
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()


def fake_categories(count=10):
    category = Category(name='Default')
    db.session.add(category)
    for i in range(count):
        category = Category(name=fake.word())
        db.session.add(category)
    db.session.commit()

def fake_post(count=50):
    for i in range(count):
        post = Post(
            title=fake.sentence(),
            body=fake.text(2000),
            category=Category.query.get(random.randint(1, Category.query.count())),
            timestamp=fake.date_time_this_year(),
            author = User.query.get(random.randint(1, User.query.count()))
        )
        db.session.add(post)
    db.session.commit()

# def fake_collect(count=50):
#     for i in range(count):
#         user = User.query.get(random.randint(1, User.query.count()))
#         user.collect(Post.query.get(random.randint(1, Post.query.count())))
#     db.session.commit()

def fake_comment(count=500):
    for i in range(count):
        comment = Comment(
            author=User.query.get(random.randint(1, User.query.count())),
            body=fake.sentence(),
            timestamp=fake.date_time_this_year(),
            post=Post.query.get(random.randint(1, Post.query.count()))
        )
        db.session.add(comment)
    db.session.commit()