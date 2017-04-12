#!/usr/bin/env python
import os

from flask.ext.script import Manager, Shell, Server
from flask.ext.migrate import Migrate, MigrateCommand

from app import create_app, db
from app.models import User, Role, Permission, Blog
from app.tools import mylogger

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Blog=Blog)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
# REBOL note, threaded=True, 多次点击就不会卡住
server = Server(host="0.0.0.0", port=80, threaded=True)
manager.add_command("runserver", server)

@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def make_admin():
    Role.insert_roles()
    Role.query.all()

    user = User(email='rebol@126.com',
                    username='rebolomo',
                    password='123456',
                    confirmed=True,)
    db.session.add(user)
    db.session.commit()



if __name__ == '__main__':
    mylogger.addconsole()
    manager.run()
