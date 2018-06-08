import os
import hashlib
import time

from datetime import datetime
from . import admin
from ..models import Article, User, Tags, Classify, Archive
from .. import UPLOAD_DIR, ADMIN_KEY, FLASK_KEY, db
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import render_template, request, url_for, jsonify, redirect, abort
from collections import deque

# admin 主页最近动作
recent_action = deque(maxlen=10)


@admin.before_request
def auth_admin():
	# admin 下每个请求会先经过这个函数 类似中间件
	# 检查cookie 与cookie的值
	# 正常就不用管 否则就转到admin登录页

	admin_cookie = request.cookies.get('admin')
	if not admin_cookie:
		return redirect(url_for('auth.admin_login'))
	s = Serializer(FLASK_KEY)
	try:
		admin_sha1 = s.loads(admin_cookie)['admin']
	except:
		return redirect(url_for('auth.admin_login'))
	if admin_sha1 != hashlib.sha1(ADMIN_KEY.encode('utf-8')).hexdigest():
		return redirect(url_for('auth.admin_login'))


@admin.route('/')
def index():
	model_names = ['article', 'tags', 'classify', 'archive', 'user']
	return render_template('admin/index.html', model_names=model_names, recent_action=recent_action)


@admin.route('/models/<model_name>')
@admin.route('/models/<model_name>/<int:page>')
def models(model_name, page=1):
	# model 列表页 and 分页

	if model_name == 'user':
		pagination = User.query.paginate(page, 20, error_out=True)
	elif model_name == 'article':
		pagination = Article.query.order_by(Article.create_at.desc()).paginate(page, 20, error_out=True)
	elif model_name == 'tags':
		pagination = Tags.query.paginate(page, 20, error_out=True)
	elif model_name == 'classify':
		pagination = Classify.query.paginate(page, 20, error_out=True)
	elif model_name == 'archive':
		pagination = Archive.query.paginate(page, 20, error_out=True)
	else:
		abort(400)

	return render_template('admin/model_list.html', pagination=pagination, model_name=model_name)


@admin.route('/delete', methods=['POST'])
def delete():
	global recent_action

	# 删除选中的model
	id_list = request.form.get('id_list')
	model_name = request.form.get('model_name')
	if model_name == 'user':
		delete_model = 'User.query.filter_by(id={id}).first()'
	elif model_name == 'article':
		delete_model = 'Article.query.filter_by(id={id}).first()'
	elif model_name == 'classify':
		delete_model = 'Classify.query.filter_by(id={id}).first()'
	elif model_name == 'archive':
		delete_model = 'Archive.query.filter_by(id={id}).first()'
	elif model_name == 'tags':
		delete_model = 'Tags.query.filter_by(id={id}).first()'
	else:
		abort(400)

	for id in id_list.split(','):
		model = eval(delete_model.format(id=id))
		if model.__tablename__ == 'user':
			recent_action.append([3, model.name, model.__tablename__])
		else:
			recent_action.append([3, model.title, model.__tablename__])
		db.session.delete(model)
	db.session.commit()
	return jsonify('result', True)


@admin.route('/editor_model/<model_name>', methods=['GET', 'POST'])
@admin.route('/editor_model/<model_name>/<model_id>', methods=['GET', 'POST'])
def editor_model(model_name, model_id=None):
	global recent_action

	# 无id 添加新的model
	# 有id 修改指定的model

	# get
	if request.method == 'GET':
		if model_id:
			# 有id 返回根据id 查询到的model
			action = '修改'
			if model_name == 'tags':
				model = Tags.query.filter_by(id=model_id).first()
			elif model_name == 'classify':
				model = Classify.query.filter_by(id=model_id).first()
			elif model_name == 'archive':
				model = Archive.query.filter_by(id=model_id).first()
			elif model_name == 'article':
				model = Article.query.filter_by(id=model_id).first()
			else:
				abort(400)
		# 否则不返回
		else:
			action = '添加'
			model = None
		if model_name == 'article':
			tags_list = Tags.query.all()
			archive_list = Archive.query.all()
			classify_list = Classify.query.all()
		else:
			classify_list = None
			archive_list = None
			tags_list = None
		return render_template('admin/editor.html', model_name=model_name, action=action, model=model,
		                       archive_list=archive_list, classify_list=classify_list, tags_list=tags_list)

	# post
	# 有id 就修改 id查询到的model
	recent = []

	if model_id:
		recent.append(2)
		if model_name == 'article':
			model = Article.query.filter_by(id=model_id).first()
		elif model_name == 'tags':
			model = Tags.query.filter_by(id=model_id).first()
		elif model_name == 'classify':
			model = Classify.query.filter_by(id=model_id).first()
		elif model_name == 'archive':
			model = Archive.query.filter_by(id=model_id).first()
		else:
			abort(400)

	# 否则创建一个新的model
	else:
		recent.append(1)
		if model_name == 'tags':
			model = Tags()
		elif model_name == 'classify':
			model = Classify()
		elif model_name == 'article':
			model = Article()
		elif model_name == 'archive':
			model = Archive()
		else:
			abort(400)

	model.title = request.form.get('title')
	if model_name == 'article':
		model.create_at = time.time()
		model.content = request.form.get('content')
		model.classify_id = request.form.get('classify')
		model.archive_id = request.form.get('archive')
		tags_ids = request.form.getlist('tags')
		# 先删除之前的
		for tags in model.tags_list.all():
			model.tags_list.remove(tags)
		# 然后添加修改之后的
		for tags_id in tags_ids:
			model.tags_list.append(Tags.query.filter_by(id=tags_id).first())

	db.session.add(model)
	db.session.commit()
	recent.extend([model.title, model.__tablename__])
	recent_action.append(recent)

	# 1返回admin主页 2返回当前的model_id 3创建一个新的model
	btn = request.form.get('btn')
	if int(btn) == 1:
		return redirect(url_for('.index'))
	elif int(btn) == 2:
		return redirect(url_for('.editor_model', model_name=model_name, model_id=model.id))
	elif int(btn) == 3:
		return redirect(url_for('.editor_model', model_name=model_name))


@admin.route('/upload', methods=['POST'])
def upload():
	# editor.md 上传图片

	file = request.files.get('editormd-image-file')
	if not file:
		result = {
			'success': 0,
			'message': u'图片格式异常'
		}
	else:
		ex = os.path.splitext(file.filename)[1]
		img = datetime.now().strftime('%Y%m%d%H%M%S')+ex

		file.save(os.path.join(UPLOAD_DIR, img))
		result = {
			'success': 1,
			'message': u'图片上传成功',
			'url': url_for('static', filename='/static/upload/'+img)
		}
	return jsonify(result)
