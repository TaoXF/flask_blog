from app import app, db
from app.models import Article, Tags, Classify, Archive
from flask_script import Manager, Shell
from flask_migrate import MigrateCommand, Migrate

app = app.create_app('development')
manager = Manager(app)
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


# shell命令 自动导入
def make_shell_context():
    return dict(app=app, db=db, Article=Article, Archive=Archive,Tags=Tags, Classify=Classify)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

if __name__ == '__main__':
    manager.run()