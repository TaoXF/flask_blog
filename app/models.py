import time

from . import db
from . import login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(20), unique=True, index=True)
	head_pic = db.Column(db.String(200), unique=True)
	email = db.Column(db.String(64), unique=True, index=True)
	password_hash = db.Column(db.String(128))
	comment_list = db.relationship('Comment', backref='user', lazy='dynamic')

	def __repr__(self):
		return '<user %s>' % self.name

	@property
	def password(self):
		raise AttributeError('password is not a readable attribute')

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)


# 用户验证回调函数 必须返回用户或者None
@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


class Classify(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(20), unique=True)
	article_list = db.relationship('Article', backref='classify', lazy='dynamic')


class Archive(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(20), unique=True)
	article_list = db.relationship('Article', backref='archive', lazy='dynamic')


tags_to_article = db.Table('registrations',
                           db.Column('tags_id', db.Integer, db.ForeignKey('tags.id')),
                           db.Column('article_id', db.Integer, db.ForeignKey('article.id'))
                           )


class Tags(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(20), unique=True)


class Article(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String(30), unique=True)
	content = db.Column(db.Text)
	create_at = db.Column(db.String(20))
	classify_id = db.Column(db.Integer, db.ForeignKey('classify.id'))
	archive_id = db.Column(db.Integer, db.ForeignKey('archive.id'))
	comment_list = db.relationship('Comment', backref='article', lazy='dynamic')
	tags_list = db.relationship('Tags', secondary=tags_to_article,
	                            backref=db.backref('article_list', lazy='dynamic'),
	                            lazy='dynamic')


class Comment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.String(200))
	create_at = db.Column(db.String(20))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'))