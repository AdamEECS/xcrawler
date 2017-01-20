from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from sqlalchemy.exc import IntegrityError
import json
import os
import requests
import time

app = Flask(__name__)
db_path = 'qzone.sqlite'
db = SQLAlchemy()
manager = Manager(app)

_account = {
    'uin': '3356008645',
    'g_tk': '1620541943',
    'limit': 8820,
}
_headers = {
    'Cookie': 'zzpaneluin=; zzpanelkey=; pgv_pvi=5725506560; pgv_si=s2627557376; ptui_loginuin=3356008645; ptisp=ctc; RK=nhFaze4r20; ptcz=09cfe05d99faf4a12525f5e34f5414444f6160c78e8bcd72b2114991e87ce488; pt2gguin=o3356008645; uin=o3356008645; skey=@MOLTRnaf7; p_uin=o3356008645; p_skey=O8C38-bKy3A6lxVCR*88*n1VX1OKUs0psf57Mvo3EHw_; pt4_token=ZQj7ND62G67RVslX026Ik3etf0ZqyVY5QmZeFIkI5ME_; pgv_pvid=5621453928; pgv_info=ssid=s485117351; qzspeedup=sdch',
}


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


class Userinfo(db.Model, Model):
    __tablename__ = 'userinfo'

    id = db.Column(db.Integer, primary_key=True)
    uin = db.Column(db.Text)
    is_famous = db.Column(db.Text)
    famous_custom_homepage = db.Column(db.Text)
    nickname = db.Column(db.Text)
    emoji = db.Column(db.Text)
    spacename = db.Column(db.Text)
    desc = db.Column(db.Text)
    signature = db.Column(db.Text)
    avatar = db.Column(db.Text)
    sex_type = db.Column(db.Text)
    sex = db.Column(db.Text)
    animalsign_type = db.Column(db.Text)
    constellation_type = db.Column(db.Text)
    constellation = db.Column(db.Text)
    age_type = db.Column(db.Text)
    age = db.Column(db.Text)
    islunar = db.Column(db.Text)
    birthday_type = db.Column(db.Text)
    birthyear = db.Column(db.Text)
    birthday = db.Column(db.Text)
    bloodtype = db.Column(db.Text)
    address_type = db.Column(db.Text)
    country = db.Column(db.Text)
    province = db.Column(db.Text)
    city = db.Column(db.Text)
    home_type = db.Column(db.Text)
    hco = db.Column(db.Text)
    hp = db.Column(db.Text)
    hc = db.Column(db.Text)
    marriage = db.Column(db.Text)
    career = db.Column(db.Text)
    company = db.Column(db.Text)
    cco = db.Column(db.Text)
    cp = db.Column(db.Text)
    cc = db.Column(db.Text)
    cb = db.Column(db.Text)
    mailname = db.Column(db.Text)
    mailcellphone = db.Column(db.Text)
    mailaddr = db.Column(db.Text)
    qzworkexp = db.Column(db.Text)
    qzeduexp = db.Column(db.Text)
    ptimestamp = db.Column(db.Text)

    def __init__(self, form):
        for k, v in form.items():
            self.__dict__[k] = str(v)
        self.id = int(self.uin)


def request_get(url, query=None):
    if query is None:
        query = {}
    r = requests.get(url, params=query, headers=_headers)
    r = r.content.decode()
    # print(r)
    r_json = r.split('Callback(')[1]
    r_json = r_json[0:-3]
    return r_json


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


def get_userinfo(user):
    url = 'http://h5.qzone.qq.com/proxy/domain/base.qzone.qq.com/cgi-bin/user/cgi_userinfo_get_all'
    query = {
        'uin': user.id,
        'vuin': _account['uin'],
        'g_tk': _account['g_tk'],
    }
    r = request_get(url, query)
    r_dict = json.loads(r)
    userinfo = Userinfo(r_dict)
    userinfo.save()


def get_userinfo_all():
    users = Person.query.all()
    i = 0
    num = 8820
    num_got = 4263
    for user in users:
        if i < 8820:
            i += 1
            continue
        exist = Userinfo.query.get(user.id)
        if exist is not None:
            continue
        try:
            get_userinfo(user)
            num_got += 1
            print('got one: ', num_got)
        except UnicodeDecodeError:
            pass
        except:
            pass
        finally:
            num += 1
            print('total: ', num)
            time.sleep(3)


@manager.command
def main():
    # import_group('jsoncache/qq_3411624395=groups.json')
    # import_person('jsoncache/')
    get_userinfo_all()


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    main()
