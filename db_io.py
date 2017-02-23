from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
import json
import os
import requests
import time

app = Flask(__name__)
db_path = 'qq20170204.db'
db = SQLAlchemy()
manager = Manager(app)

_account = {
    'uin': '3411624395',
    'g_tk': '321064777',
    'limit': 0,
}
_headers = {
    'Cookie': 'pgv_pvid=1160608280; pgv_info=ssid=s6207716200; ptui_loginuin=3411624395; ptisp=ctc; RK=ny1KTbIf2w; ptcz=26ce7bea8dfddb6d168f01552d5f10bd95239bfbc29732e5addd91e46c19ee93; pt2gguin=o3411624395; uin=o3411624395; skey=@duHJMHXzP; p_uin=o3411624395; p_skey=od0CRgXVqB*g*axXe80bY5z0aZJayWqT74ZTyFe6GVg_; pt4_token=g01P1MfhGPjrvfYeJvHVN3dAaSRdPzr77LJKm4av9NE_; fnc=2; Loading=Yes; qzspeedup=sdch; QZ_FE_WEBP_SUPPORT=1',
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
    __tablename__ = 'person_all'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    tag = db.Column(db.Text)
    have_detail = db.Column(db.Integer, default=0)

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


def import_person_single(path, file, tag):
    filename = path + file
    array = open_json(filename)
    array = array['data']['item']
    for i in array:
        p = Person(i)
        p.tag = tag
        exist = Person.query.get(p.id)
        if exist is None:
            db.session.add(p)
            t = time.time()
            print('save one', t)


def import_person(path, tag):
    files = os.listdir(path)
    num = 0
    for file in files:
        if len(file) < 30:
            continue
        import_person_single(path, file, tag)
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
    users = Person.query.filter(Person.have_detail == 0).all()
    num = 1051
    num_got = 462
    for user in users:
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
            user.have_detail = 1
            user.save()
            num += 1
            print('total: ', num)
            time.sleep(1.5)


def import_person_all():
    path_list = [
        ('jsondata0208/gupiao1_111514/', '股票'),
        ('jsondata0208/gupiao2_110711/', '股票'),
        ('jsondata0208/huangjin_100080/', '黄金'),
        ('jsondata0208/xianhuo_74759/', '现货'),
    ]
    for path, tag in path_list:
        import_person(path, tag)
    # haven't commit yet
    db.session.commit()


@manager.command
def main():
    # import_group('jsoncache/qq_3411624395=groups.json')
    # import_person('jsoncache0120/')
    get_userinfo_all()
    # import_person_all()


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    main()
