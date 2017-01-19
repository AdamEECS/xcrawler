from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import json
import os

app = Flask(__name__)
db_path = 'qzone.sqlite'
db = SQLAlchemy()
manager = Manager(app)


def configure_app():
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.secret_key = 'super secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
    db.init_app(app)


def configure_manager():
    Migrate(app, db)
    manager.add_command('db', MigrateCommand)


class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = ({1})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{0}:\n  {1}\n>'.format(class_name, '\n  '.join(properties))

    def save(self):
        db.session.add(self)
        db.session.commit()


class Group(db.Model, Model):
    __tablename__ = 'group'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, form):
        self.id = form.get('groupid')
        self.name = form.get('groupname')


class Person(db.Model, Model):
    __tablename__ = 'person'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)

    def __init__(self, form):
        self.id = form.get('uin')
        self.name = form.get('nick')


def open_json(filename):
    with open(filename, encoding='utf-8') as f:
        text = f.read()
        array = json.loads(text)
        return array


def import_group(filename):
    array = open_json(filename)
    array = array['data']['group']
    for i in array:
        g = Group(i)
        g.save()


def import_person_single(path, file):
    filename = path + file
    array = open_json(filename)
    array = array['data']['item']
    for i in array:
        p = Person(i)
        exist = Person.query.get(p.id)
        if exist is None:
            p.save()
            print('save one')


def import_person(path):
    files = os.listdir(path)
    num = 0
    for file in files:
        if len(file) < 30:
            continue
        import_person_single(path, file)
        num += 1
        print(num)
        print(file)


@manager.command
def main():
    # import_group('jsoncache/qq_3411624395=groups.json')
    import_person('jsoncache/')


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    main()
