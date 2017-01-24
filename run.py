import requests
import json
import time

__author__ = '3000'
_account = {
    'uin': '2070428977',
    'g_tk': '1936570685',
}
_headers = {
    'Cookie': 'pgv_pvi=9962304512; pgv_si=s8613456896; ptui_loginuin=2070428977; ptisp=ctc; RK=nhVu4XNfel; ptcz=bd1e970c616b32b087aab5262b751a937c30e750fa1808ac519de6022183a628; pt2gguin=o2070428977; uin=o2070428977; skey=@gi8xemvke; p_uin=o2070428977; p_skey=FC965E7yfOSS6da3JT2dHy5S5i5iEDpWueZxWhGpacA_; pt4_token=NdJ8ZFejw2TQmJQa0tsVBhjj0CqQrkLAcr3xrdrmixU_; pgv_pvid=2335499456; pgv_info=ssid=s5033538176',
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
    with open('jsondata0124/p2p/{}.json'.format(name), 'w', encoding='utf-8') as f:
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
    print(r_dict['data']['group_name'])
    members_json = json.dumps(r_dict, ensure_ascii=False, indent=4)
    name = 'qq_{}=group_{}=total_{}'.format(_account['uin'], group['groupid'], r_dict['data']['total'])
    save_json(members_json, name)


def start_crawler():
    groups = get_all_group()
    num = 0
    for group in groups:
        try:
            get_member_from_group(group)
            num += 1
            print(num)
            time.sleep(1)
        except UnicodeDecodeError:
            print('UnicodeDecodeError')
        except :
            print('other error')


def main():
    start_crawler()


if __name__ == '__main__':
    main()
