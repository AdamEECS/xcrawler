import requests
import json
import time

__author__ = '3000'
_account = {
    'uin': '2242857468',
    'g_tk': '1824438566',
}
_headers = {
    'Cookie': 'pgv_pvi=6242658304; ptisp=cn; pgv_si=s2404616192; ptui_loginuin=2242857468; RK=qfOvDwK79c; ptcz=907357762bf12f526c2733ebea1252e4ad6a464c807f14de01af558235eb2af2; pt2gguin=o2242857468; uin=o2242857468; skey=@LGZnxOOW9; p_uin=o2242857468; p_skey=Z2X59phi*l2eH1jQdKQkfjAFrkNMpAnjBkgLeGVCCyY_; pt4_token=gejSQxSUhOhVvGfQUdxuHW9*6sPR6LIz1thIQJxIL1U_; pgv_pvid=4687343128; pgv_info=ssid=s506197068',
    'Host': 'qun.qzone.qq.com',
    'Upgrade - Insecure - Requests': '1',
    'Referer': 'http://ui.ptlogin2.qq.com/cgi-bin/login?appid=549000912&daid=5&style=12&s_url=http://qun.qzone.qq.com/group',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def timestamp():
    return int(time.time())


def request_get(url, query=None):
    if query is None:
        query = {}
    r = requests.get(url, params=query, headers=_headers)
    r = r.content.decode()
    r_json = r.split('Callback(')[1]
    r_json = r_json[0:-2]
    return r_json


def save_json(r, name='qq'):
    with open('jsoncache/{}.json'.format(name), 'w', encoding='utf-8') as f:
        f.write(r)


def get_all_group():
    url = 'http://qun.qzone.qq.com/cgi-bin/get_group_list'
    query = {
        'groupcount': '',
        'count': '',
        'callbackFun': '_GetGroupPortal',
        'uin': _account['uin'],
        'g_tk': _account['g_tk'],
        'ua': 'Mozilla%2F5.0%20(Macintosh%3B%20Intel%20Mac%20OS%20X%2010_12_1)%20AppleWebKit%2F537.36%20(KHTML%2C%20like%20Gecko)%20Chrome%2F55.0.2883.95%20Safari%2F537.36',
    }
    r = request_get(url, query)
    r_dict = json.loads(r)
    groups = r_dict['data']['group']
    groups_json = json.dumps(r_dict, ensure_ascii=False, indent=4)
    save_json(groups_json, 'qq_{}=groups'.format(_account['uin']))
    return groups


def get_member_from_group(group):
    url = 'http://qun.qzone.qq.com/cgi-bin/get_group_member'
    query = {
        'groupid': group['groupid'],
        'uin': _account['uin'],
        'g_tk': _account['g_tk'],
    }
    r = request_get(url, query)
    r_dict = json.loads(r)
    print(r_dict)
    members_json = json.dumps(r_dict, ensure_ascii=False, indent=4)
    name = 'qq_{}=group_{}=total_{}'.format(_account['uin'], group['groupid'], r_dict['data']['total'])
    save_json(members_json, name)


def start_crawler():
    groups = get_all_group()
    for group in groups:
        get_member_from_group(group)
        time.sleep(3)


def main():
    start_crawler()


if __name__ == '__main__':
    main()
