import random
import hashlib

from . import auth
from .. import db, ADMIN_KEY, FLASK_KEY
from ..email import send_mail
from ..models import User

from flask import render_template, jsonify, request, redirect, url_for, make_response
from flask_login import login_user, logout_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer


@auth.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))


@auth.route('/send_auth_code', methods=['POST'])
def send_auth_code():
	# 调用celery 发送随机生成的验证码
	# 并返回token 与 邮箱地址
	# t 就是加密之后的验证码
	# 用于验证用户输入的验证码是否正确与过期
	# email2 用于记录正确的邮箱地址
	# 防止获取验证码之后又提交一个无效的邮箱地址

	email = request.form.get('email')

	auth_code = ''.join(random.sample(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'], 6))
	s = Serializer(FLASK_KEY, 300)
	token = s.dumps({'token': auth_code})
	send_mail(auth_code, email)
	return jsonify({'t': token.decode('utf-8'), 'email2': email})


@auth.route('/login', methods=['GET', 'POST'])
def login():
	# 根据邮箱进行查找用户
	# verify_password 是flask_login模块的验证函数
	# login_user() 也是flask_login模块的函数用于记住用户是否登录

	if request.method == 'GET':
		return render_template('auth/login.html')
	pwd = request.form.get('pwd')
	email = request.form.get('email')

	user = User.query.filter_by(email=email).first()
	if not user:
		return jsonify({'error': 'email_error', 'reason': '邮箱错误'})
	if not user.verify_password(password=pwd):
		return jsonify({'error': 'pwd_error', 'reason': '密码错误'})
	login_user(user)
	return jsonify({'error': False})


@auth.route('/register', methods=['GET', 'POST'])
def register():
	# 当所有验证通过才会添加到数据库

	if request.method == 'GET':
		return render_template('auth/register.html')
	t = request.form.get('t')
	name = request.form.get('name')
	pwd = request.form.get('pwd')
	email = request.form.get('email')
	email2 = request.form.get('email2')
	auth_code = request.form.get('auth_code')

	s = Serializer(FLASK_KEY)
	try:
		token = s.loads(t)['token']
	except:
		return jsonify({'error': 'auth_code_error', 'reason': '验证码已过期'})
	if auth_code != token:
		return jsonify({'error': 'auth_code_error', 'reason': '验证码错误'})

	if 0 != User.query.filter_by(name=name).count():
		return jsonify({'error': 'name_error', 'reason': '用户名已存在'})
	if 0 != User.query.filter_by(email=email).count():
		return jsonify({'error': 'email_error', 'reason': '该邮箱已注册'})
	if email != email2:
		return jsonify({'error': 'email2_error', 'reason': '请提交正确的邮箱地址'})

	user = User()
	user.name = name
	user.name = name
	user.email = email
	user.password = pwd

	# 用户头像
	url = 'http://gravatar.com/avatar/{hash}?s={size}&d=identicon&r=g'
	hash_ = hashlib.md5(email.encode('utf-8')).hexdigest()
	user.head_pic = url.format(hash=hash_, size=256)

	db.session.add(user)
	db.session.commit()
	login_user(user)
	return jsonify({'error': False})


@auth.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
	# admin_登录路由函数
	# 检查输入 正确就设置cookie
	# 然后转到admin_index
	if request.method == 'GET':
		return render_template('auth/login_admin.html')
	admin_sha1 = request.form.get('admin')
	if not admin_sha1:
		return '输入错误~~'
	if admin_sha1 != hashlib.sha1(ADMIN_KEY.encode('utf-8')).hexdigest():
		return '输入错误~~'
	s = Serializer(FLASK_KEY, 60*60*24)
	admin = s.dumps({'admin': admin_sha1})
	response = make_response(redirect(url_for('admin.index')))
	response.set_cookie('admin', admin.decode('utf-8'))
	return response


@auth.route('/admin_logout')
def admin_logout():
	response = make_response(redirect(url_for('admin.index')))
	response.delete_cookie('admin')
	return response

