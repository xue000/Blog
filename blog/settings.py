import os
import sys

basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# SQLite URI compatible
WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'


class Operations:
    CONFIRM = 'confirm'
    RESET_PASSWORD = 'reset-password'
    CHANGE_EMAIL = 'change-email'
    CHANGE_PASSWORD = 'change-password'


class BaseConfig:
    BLOG_ADMIN_EMAIL = os.getenv('BLOG_ADMIN', 'admin@helloflask.com')
    BLOG_POST_PER_PAGE = 10
    BLOG_SEARCH_RESULT_PER_PAGE = 20
    BLOG_COMMENT_PER_PAGE = 15
    BLOG_USER_PER_PAGE = 20
    BLOG_MANAGE_USER_PER_PAGE = 30
    BLOG_MANAGE_CATEGORY_PER_PAGE = 50
    BLOG_MANAGE_POST_PER_PAGE = 20
    BLOG_MANAGE_COMMENT_PER_PAGE = 30
    BLOG_MAIL_SUBJECT_PREFIX = '[Blog]'

    SECRET_KEY = os.getenv('SECRET_KEY', 'secret string')
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # file size exceed to 3 Mb will return a 413 error response.

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('Albumy Admin', MAIL_USERNAME)

    WHOOSHEE_MIN_STRING_LEN = 1

class DevelopmentConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = \
        prefix + os.path.join(basedir, 'data-dev.db')
    REDIS_URL = "redis://localhost"


class TestingConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///'  # in-memory database


class ProductionConfig(BaseConfig):
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',
                                        prefix + os.path.join(basedir, 'data.db'))
    SQLALCHEMY_POOL_RECYCLE = 280

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
