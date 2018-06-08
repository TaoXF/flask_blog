from flask_mail import Message
from . import app, mail

celery = app.create_celery()


@celery.task
def send_mail(auth_code, email):
	msg = Message('验证码', sender='2811262194@qq.com', recipients=[email])
	msg.body = '验证码'
	msg.html = auth_code
	mail.send(msg)