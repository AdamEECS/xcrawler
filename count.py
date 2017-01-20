import os
import json


def count_all(path):
    files = os.listdir(path)
    print(files)
    total_all = 0
    total_list = []
    for name in files:
        if len(name) < 30:
            continue
        total = name.split('=')[2]
        total = total.split('_')[1]
        total = total.split('.')[0]
        total = int(total)
        total_all += total
        total_list.append(total)
    print(total_all)
    print(total_list)
    group_by(total_list)


def group_by(array):
    n2, n5, n10, n15, n20 = 0, 0, 0, 0, 0
    for i in array:
        if i < 200:
            n2 += 1
        elif i < 500:
            n5 += 1
        elif i < 1000:
            n10 += 1
        elif i < 1500:
            n15 += 1
        else:
            n20 += 1
    print(n2, n5, n10, n15, n20)


def open_json(filename):
    with open(filename, encoding='utf-8') as f:
        text = f.read()
        array = json.loads(text)
        array = array['data']['group']
        print(array)


def main():
    path = "E:/xcrawler/jsoncache0120"
    count_all(path)
    # file = '/qq_3411624395=groups.json'
    # filename = path + file
    # open_json(filename)


if __name__ == '__main__':
    main()
