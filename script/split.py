import numpy as np
import pandas as pd
import os


def read(path):
    f = open(path, 'r')
    l = f.readline()
    l = f.readline()
    print(l)
    # res = []
    while l:
        print(l)
        l = f.readline()
    #     l = str(l).split(' ')
    # #     tmp = []
    # #     for item in l:
    # #         item = item.split('/')
    # #         tmp.append(item[-1][:-1])
    # #     res.append(tmp)
    # #     l = f.readline()
    # count = 0
    # miao = 1
    # while count < 150000 and l:
    #     test = open('data/split'+str(miao)+'.txt', 'a')
    #     l = str(l)
    #     # print(l)
    #     print("count: {0} , miao: {1}".format(count, miao))
    #     test.write(l+'\n')
    #     l = f.readline()
    #     count += 1
    #     if count == 150000:
    #         count = 0
    #         miao += 1

    # res = pd.DataFrame(res)
    # res.to_csv('split.csv')


def split(path):
    for i in range(1, 126):
        f = open(path+'split'+str(i)+'.txt', 'r')
        w = open(path+'res'+str(i)+'.txt', 'w')
        l = f.readline()
        while l:
            l = l.split(' ')
            tmp = ""
            for item in l:
                item = item.split('/')
                tmp += item[-1][:-1] + ","
            if len(tmp) == 1:
                l = f.readline()
                continue
            else:
                w.write(tmp[:-3]+'\n')
                l = f.readline()
        print("Res: {}".format(i))
        w.close()


def test(path):
    data = pd.read_csv('split.csv')
    print(data.iloc[1:10])


if __name__ == '__main__':
    read('mappingbased_objects_en.ttl')
    # test('split.csv')
    # split('data/')