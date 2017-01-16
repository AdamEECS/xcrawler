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

_headers = {
    'Cookie': 'pgv_pvi=6242658304; ptisp=cn; pgv_si=s2404616192; ptui_loginuin=2242857468; RK=qfOvDwK79c; ptcz=907357762bf12f526c2733ebea1252e4ad6a464c807f14de01af558235eb2af2; pt2gguin=o2242857468; uin=o2242857468; skey=@LGZnxOOW9; p_uin=o2242857468; p_skey=Z2X59phi*l2eH1jQdKQkfjAFrkNMpAnjBkgLeGVCCyY_; pt4_token=gejSQxSUhOhVvGfQUdxuHW9*6sPR6LIz1thIQJxIL1U_; pgv_pvid=4687343128; pgv_info=ssid=s506197068',
    'Host': 'qun.qzone.qq.com',
    'Upgrade - Insecure - Requests': '1',
    'Referer': 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&daid=5&style=12&s_url=http://qun.qzone.qq.com/group',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}
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
    qq = db.Column(db.Integer)
    name = db.Column(db.Text)
    allow = db.Column(db.Boolean)
    comment = db.Column(db.Text)
    created_time = db.Column(db.Integer, default=0)

    def __init__(self):
        self.id = -1
        self.qq = -1
        self.name = ''
        self.comment = ''
        self.created_time = timestamp()


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


def request_get(url, query={}, headers=_headers):
    r = requests.get(url, params=query, headers=headers)
    r = r.content.decode()
    rjson = r.split('Callback(')[1]
    rjson = rjson[0:-2]
    save_json(rjson, name='qun_member')


def save_json(r, name='qq'):
    t = timestamp()
    with open('htmlcache/{}_{}.json'.format(name, t), 'w', encoding='utf-8') as f:
        f.write(r)


def read_json():
    with open('htmlcache/qq_main_1484534675.json', 'r', encoding='utf-8') as f:
        rjson = f.read()
    rdict = json.loads(rjson)
    group = rdict['data']['group']
    for i in group:
        print(i['groupid'])


def get_member_from_group(uin='2242857468', groupid='347842957', g_tk='1824438566'):
    url = 'http://qun.qzone.qq.com/cgi-bin/get_group_member'
    query = {
        'callbackFun': '_GroupMember',
        'uin': uin,
        'groupid': groupid,
        'neednum': '1',
        'g_tk': g_tk,
        'ua': 'Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_12_1)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F55.0.2883.95%20Safari%2F537.36'
    }

    request_get(url, query, _headers)


def read_html(i):
    i = str(i)
    with open('davv_{}.html'.format(i), 'r', encoding='utf-8') as f:
        for line in f.readlines()[149:150]:
            r = line
            divs_from_html(r)


def requests_with_headers(url):

    # divs_from_url(url, headers)
    request_get(url, headers=_headers)


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
    # pages = 4
    # url = 'http://weibo.com/p/1035052887339314/follow?pids=Pl_Official_HisRelation__61&relate=fans&page={}&ajaxpagelet=1&ajaxpagelet_v6=1&__ref=%2Fp%2F1035052887339314%2Ffollow%3Frelate%3Dfans%26from%3D103505%26wvr%3D6%26mod%3Dheadfans%26current%3Dfans%23place&_t=FM_148282001854539'.format(pages)
    # for i in range(39, 52):
    #     url = 'http://s.weibo.com/user/%25E9%2587%2591%25E8%259E%258D&page=' + str(i)
    #     requests_with_headers(url)
    # for i in range(39, 51):
    #     read_html(i)
    # fanshtml_from_davv()

    # url = 'http://qun.qzone.qq.com/cgi-bin/get_group_list?groupcount=4&count=4&callbackFun=_GetGroupPortal&uin=2242857468&g_tk=1824438566&ua=Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_12_1)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F55.0.2883.95%20Safari%2F537.36'
    # requests_with_headers(url)

    # read_json()
    get_member_from_group()


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    main()
