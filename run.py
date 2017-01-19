import requests
import json
import time

__author__ = '3000'
_account = {
    'uin': '3411624395',
    'g_tk': '103183856',
}
_headers = {
    'Cookie': 'cpu_performance=51; _gscu_661903259=42817501ey2bda90; pgv_pvi=1397720064; RK=nlNqYajjSv; pac_uid=1_986523974; tvfe_boss_uuid=daff260f2959cf25; o_cookie=986523974; pgv_pvid=2388668785; pgv_si=s9370320896; pgv_info=ssid=s946051304; QZ_FE_WEBP_SUPPORT=1; cpu_performance_v8=30; qzspeedup=sdch; qqmusic_uin=; qqmusic_key=; qqmusic_fromtag=; qzmusicplayer=qzone_player_8637650_1484275768276; rv2=80CC32496881903EAD7468C947DDE2C862DA8FF86107325304; property20=786849BF82F574FDC7FFABAD75682A5647F288E1834F2D6728C500B3F599A723E51B95D33EE24303; __Q_w_s__QZN_TodoMsgCnt=1; logout_page=; dm_login_weixin_rem=; qm_authimgs_id=1; qm_verifyimagesession=h01f9a61c66c2d109568cb7af087a3b1a7618f03cf1c481edd65cbf19250b15bb74148ba693df94c826; ptui_loginuin=3411624395; ptisp=ctc; ptcz=919ce23c00eb03241bc6af35e47843d81951168b3d026d6112a4b24b5c038854; pt2gguin=o3411624395; uin=o3411624395; skey=@ptfB5CqBT; p_uin=o3411624395; p_skey=9Xwi06COjSEUXHOgXatxJ-*BlsXKNMiN-lUIHTU61Hg_; pt4_token=loKCD5i2bSSzQcKivQOw*2PH36mxcJTgb8KhEi-ASm0_',
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
