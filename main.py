import requests
import json
import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from lxml import html
import lxml

__author__ = '3000'
'''
账号：
密码：
'''
app = Flask(__name__)
db_path = 'weibo.sqlite'
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


def timestamp():
    return int(time.time())


class Model(object):
    def __repr__(self):
        class_name = self.__class__.__name__
        properties = ('{0} = ({1})'.format(k, v) for k, v in self.__dict__.items())
        return '\n<{0}:\n  {1}\n>'.format(class_name, '\n  '.join(properties))

    def save(self):
        db.session.add(self)
        db.session.commit()


class Person(db.Model, Model):
    __tablename__ = 'persons'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    sex = db.Column(db.Text)
    follow = db.Column(db.Text)
    fans = db.Column(db.Text)
    weibos = db.Column(db.Text)
    add = db.Column(db.Text)
    created_time = db.Column(db.Integer, default=0)

    def __init__(self):
        self.id = -1
        self.name = ''
        self.sex = ''
        self.follow = ''
        self.fans = ''
        self.weibos = ''
        self.add = ''
        self.created_time = timestamp()

    def insert(self):
        person_in_db = Person.query.get(self.id)
        if person_in_db is None:
            self.save()
        else:
            person_in_db.update(new=self)
            person_in_db.save()

    def update(self, new):
        self.name = new.name
        self.sex = new.sex
        self.follow = new.follow
        self.fans = new.fans
        self.weibos = new.weibos
        self.add = new.add
        self.created_time = new.created_time


def person_from_li(div):
    person = Person()
    data = div.xpath('./@action-data')[0]
    data = data.split('&')
    dic = {i.split('=')[0]: i.split('=')[1] for i in data}
    person.id = int(dic.get('uid', -1))
    person.name = dic.get('fnick', '')
    person.sex = dic.get('sex', '')
    person.follow = int(div.xpath('.//div[@class="info_connect"]/span/em/a')[0].text)
    person.fans = int(div.xpath('.//div[@class="info_connect"]/span/em/a')[1].text)
    person.weibos = int(div.xpath('.//div[@class="info_connect"]/span/em/a')[2].text)
    person.add = div.xpath('.//div[@class="info_add"]/span')[0].text
    person.insert()
    return person


def person_from_div(div):
    person = Person()
    # print(div.xpath('.//p[@class="person_name"]/a/@uid')[0])
    person.id = int(div.xpath('.//p[@class="person_name"]/a/@uid')[0])
    person.name = div.xpath('.//p[@class="person_name"]/a/@title')[0]
    # person.href = div.xpath('.//p[@class="person_name"]/a/@href')[0]
    person.sex = div.xpath('.//p[@class="person_addr"]/span/@title')[0]
    person.follow = div.xpath('.//p[@class="person_num"]/span/a')[0].text
    person.fans = div.xpath('.//p[@class="person_num"]/span/a')[1].text
    person.weibos = div.xpath('.//p[@class="person_num"]/span/a')[2].text
    person.add = div.xpath('.//p[@class="person_addr"]/span')[1].text
    print(person)

    person.insert()
    return person


def divs_from_url(url, headers):
    r = requests.get(url, headers=headers)
    r = r.content.decode()
    # print(r)
    r = r.split('<script>parent.FM.view(')[1]
    r = r.split(')</script>')[0]
    dict_r = json.loads(r)
    r = dict_r.get('html')
    # print(r)
    try:
        root = html.fromstring(r)
        person_divs = root.xpath('//li[@class="follow_item S_line2"]')
        persons = [person_from_li(div) for div in person_divs]
        print(len(persons))
    except lxml.etree.XMLSyntaxError:
        print(r)
        with open('log.html', 'w', encoding='utf-8') as f:
            f.write(r)


def divs_from_html(r):
    # print(r)
    r = r.split('<script>STK && STK.pageletM && STK.pageletM.view(')[1]
    r = r.split(')</script>')[0]
    dict_r = json.loads(r)
    r = dict_r.get('html')
    # print(r)

    try:
        root = html.fromstring(r)
        person_divs = root.xpath('//div[@class="person_detail"]')
        persons = [person_from_div(div) for div in person_divs]
        print(len(persons))
    except lxml.etree.XMLSyntaxError:
        print(r)
        with open('log.html', 'w', encoding='utf-8') as f:
            f.write(r)


def save_html(url, headers):
    i = url.split('page=')[1]
    r = requests.get(url, headers=headers)
    r = r.content.decode()
    with open('davv_{}.html'.format(i), 'w', encoding='utf-8') as f:
        f.write(r)


def read_html(i):
    i = str(i)
    with open('davv_{}.html'.format(i), 'r', encoding='utf-8') as f:
        for line in f.readlines()[149:150]:
            r = line
            divs_from_html(r)


def requests_with_headers(url):
    headers = {
        'Cookie': 'SINAGLOBAL=2912496465019.687.1482808897562; __gads=ID=e21cf0c1e50c0ee6:T=1482809021:S=ALNI_MYa_Eju0e69mKOBKVpe6_KF1h8xcA; un=18640346924; SCF=ArvpvuL1UzXaXmqv9Jj-NVWkl9xWv6WPLvdxFQpVyTEla-YC0kz_TyG25Nv_ztck-9i1bKHg_wT5FBMJZT7CIww.; SUHB=0nle8gO6YrdXX1; ALF=1485522084; SUB=_2A251Z8f0DeRxGeBO41EU8i7NzDSIHXVWq-m8rDV8PUJbkNAKLUL6kW0c_uu8QpOKavb_jIzB97_bYjTbNA..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFy3IlWAegLYa3r132kHbij5JpX5oz75NHD95Qcehn0SKz7eKMRWs4Dqcj.i--NiK.7iKLFi--Xi-iWi-2Ni--Xi-zRiKnNi--fiKnciKLF; UOR=www.google.com,weibo.com,m.weibo.cn; YF-Ugrow-G0=ad83bc19c1269e709f753b172bddb094; wvr=6; YF-V5-G0=b59b0905807453afddda0b34765f9151; _s_tentry=-; Apache=8027407302409.193.1483607530573; ULV=1483607530593:6:2:2:8027407302409.193.1483607530573:1483413510517; YF-Page-G0=c47452adc667e76a7435512bb2f774f3; WBtopGlobal_register_version=c689c52160d0ea3b',
        'Host': 's.weibo.com',
        'Upgrade - Insecure - Requests': '1',
        'Referer': 'http://s.weibo.com/user/%25E9%2587%2591%25E8%259E%258D&page=2',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
    }
    # divs_from_url(url, headers)
    save_html(url, headers)


def fanshtml_from_davv():
    davv_all = Person.query.all()
    # print(davv_all)
    for davv in davv_all:
        print(davv)
        url = 'http://weibo.com/p/1015073790/follow?relate=fans&from=100505&wvr=6&mod=headfans&current=fans#place'
        time.sleep(2)



@manager.command
def main():
    print('crawler run')
    pages = 4
    # url = 'http://weibo.com/p/1035052887339314/follow?pids=Pl_Official_HisRelation__61&relate=fans&page={}&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=%2Fp%2F1035052887339314%2Ffollow%3Frelate%3Dfans%26from%3D103505%26wvr%3D6%26mod%3Dheadfans%26current%3Dfans%23place&_t=FM_148282001854539'.format(pages)
    # for i in range(39, 52):
    #     url = 'http://s.weibo.com/user/%25E9%2587%2591%25E8%259E%258D&page=' + str(i)
    #     requests_with_headers(url)
    # for i in range(39, 51):
    #     read_html(i)
    fanshtml_from_davv()


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    main()
