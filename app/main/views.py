import json
import re
import time

from markdown import markdown
from utils import datetime_filter
from flask_login import current_user

from . import main
from .. import db
from ..models import User, Archive, Article, Classify, Tags, Comment
from flask import render_template, redirect, url_for, abort, request


@main.route('/')
def index():
	tags_list = Tags.query.all()
	archive_list = Archive.query.all()
	classify_list = Classify.query.all()
	pagination = Article.query.order_by(Article.create_at.desc()).paginate(1, 10, error_out=True)
	return render_template('main/index.html', tags_list=tags_list, archive_list=archive_list,
	                       classify_list=classify_list, pagination=pagination)


# 从主页翻页时不需要id 直接查找所有文章就行了
# 根据外键查找必须带上id 没有page 表示第一页
@main.route('/<model_name>/article_list/<int:page>')
@main.route('/<model_name>/<model_id>/article_list')
@main.route('/<model_name>/<model_id>/article_list/<int:page>')
def article_list(model_name, model_id=None, page=1):
	if model_name == 'default':
		pagination = Article.query.order_by(Article.create_at.desc()).paginate(page, 10, error_out=True)
	else:
		if model_id:
			if model_name == 'classify':
				pagination = Classify.query.filter_by(id=model_id).first_or_404().article_list.paginate(page, 10, error_out=True)
			elif model_name == 'tags':
				pagination = Tags.query.filter_by(id=model_id).first_or_404().article_list.paginate(page, 10, error_out=True)
			elif model_name == 'archive':
				pagination = Archive.query.filter_by(id=model_id).first_or_404().article_list.paginate(page, 10, error_out=True)
			else:
				abort(400)
		else:
			abort(400)

	articles = []
	for article in pagination.items:
		tags_list = []
		for tags in article.tags_list.all():
			tags_list.append({'title': tags.title, 'id': tags.id})
		articles.append({
			'id': article.id,
			'title': article.title,
			# 先markdown渲染 然后re剔除html标签 最后取前160 + ...
			'summary': re.sub('<[^>]+>', '', markdown(article.content))[:160] + '...',
			'create_at': datetime_filter(article.create_at),
			'classify': {'title': article.classify.title, 'id': article.classify_id},
			'tags_list': tags_list
		})

	page = {
		'has_prev': pagination.has_prev,
		'has_next': pagination.has_next,
		'now_page': pagination.page,
		'iter_pages': list(pagination.iter_pages()),
	}

	result = {
		'model_name': model_name,
		'model_id': model_id,
		'pagination': page,
		'articles': articles,
	}

	return json.dumps(result)


# 文章内容
@main.route('/article/<article_id>')
def article(article_id):
	post = Article.query.filter_by(id=article_id).first_or_404()
	tags_list = []
	for tags in post.tags_list.all():
		tags_list.append({'title': tags.title, 'id': tags.id})

	article_ = {
		'id': post.id,
		'title': post.title,
		'content': markdown(post.content),
		'create_at': datetime_filter(post.create_at),
		'tags_list': tags_list,
		'classify': {'title': post.classify.title, 'id': post.classify_id},
	}
	return json.dumps({'article': article_})


# 留言
# POST就是添加新的留言并返回第一页的数据
# GET 直接返回第一页的数据
# 有page 表示翻页
@main.route('/<article_id>/comments', methods=['GET', 'POST'])
@main.route('/<article_id>/comments/<int:page>')
def comments(article_id, page=1):
	if request.method == 'POST':
		content = request.form.get('content')
		article_id = request.form.get('article_id')
		user_id = request.form.get('user_id')
		c = Comment()
		c.content = content
		c.user_id = user_id
		c.article_id = article_id
		c.create_at = time.time()
		db.session.add(c)
		db.session.commit()

	article = Article.query.filter_by(id=article_id).first_or_404()
	is_authenticated = current_user.is_authenticated
	comment_list_ = article.comment_list
	if comment_list_.count():
		has_comment = True
		if comment_list_.count() < 10:
			comment_list_all = comment_list_.all()
			page = None
		else:
			pagination = article.comment_list.paginate(page, 10, error_out=True)
			page = {
				'has_prev': pagination.has_prev,
				'has_next': pagination.has_next,
				'now_page': pagination.page,
				'iter_pages': list(pagination.iter_pages()),
			}
			comment_list_all = pagination.items
	else:
		page = None
		has_comment = False
		comment_list_all = []

	comment_list = []
	for comment in comment_list_all:
		comment_list.append({
			'content': comment.content,
			'create_at': datetime_filter(comment.create_at),
			'user': {'head_pic': comment.user.head_pic, 'name': comment.user.name},
		})

	if is_authenticated:
		current_user_id = current_user.id,
	else:
		current_user_id = None

	result = {
		'has_comment': has_comment,
		'pagination': page,
		'comment_list': comment_list,
		'is_authenticated': is_authenticated,
		'current_user_id': current_user_id
	}
	return json.dumps(result)
