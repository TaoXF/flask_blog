
class Config(object):
	SECRET_KEY = 'csrf_key'
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True

	@staticmethod
	def init_app(app):
		pass


class DevelopmentConfig(Config):
	DEBUG = True
	MAIL_SERVER = 'smtp.qq.com'
	MAIL_PORT = 465
	MAIL_USE_SSL = True
	MAIL_USERNAME = '2811262194@qq.com'
	MAIL_PASSWORD = 'email 授权码'

	SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:mysql_pwd@127.0.0.1:3306/flask_development"


class ProductionConfig(Config):

	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql_pwd@127.0.0.1:3306/flask_Production'

config = {
	'development': DevelopmentConfig,
	'production': ProductionConfig
}
