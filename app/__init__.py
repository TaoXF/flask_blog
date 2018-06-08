import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from celery import Celery
from flask_mail import Mail

# admin登录密码
ADMIN_KEY = 'admin_password'

# 生成加密令牌的key
FLASK_KEY = 'flaks_key'

# 上传图片的保存路径
UPLOAD_DIR = os.path.abspath(os.path.dirname(__file__)) + '/static/upload/'


mail = Mail()
db = SQLAlchemy()

# 登录验证
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'


class App(object):

    def __init__(self):
        self.app = Flask(__name__, static_folder='', static_url_path='')

    def create_app(self, config_name):
        self.app.config.from_object(config[config_name])
        config[config_name].init_app(self.app)

        CSRFProtect(self.app)

        db.init_app(self.app)
        mail.init_app(self.app)
        login_manager.init_app(self.app)

        from .main import main as main_blueprint
        self.app.register_blueprint(main_blueprint)

        from .auth import auth as auth_blueprint
        self.app.register_blueprint(auth_blueprint, url_prefix='/auth')

        from .admin import admin as admin_blueprint
        self.app.register_blueprint(admin_blueprint, url_prefix='/admin')
        return self.app

    def create_celery(self):
        CELERY_BROKER_URL = 'redis://:redis_pwd@localhost:6379/0'
        CELERY_RESULT_BACKEND = 'redis://:redis_pwd@localhost:6379/0'
        celery = Celery(
            self.app.import_name,
            backend=CELERY_RESULT_BACKEND,
            broker=CELERY_BROKER_URL
        )
        celery.conf.update(self.app.config)
        app = self.app

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        celery.Task = ContextTask
        return celery


app = App()


