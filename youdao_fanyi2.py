#/usr/bin/python
# encoding:utf-8
# __Author__ = Slwhy

import requests
import time
import random
import hashlib
import json
import os
from urllib import request
import urllib
def translate(t):
    i = str(int(time.time()*1000)+random.randint(1,10))
    # t = input("please input the word you want to translate:")
    u = 'fanyideskweb'
    l = 'aNPG!!u6sesA>hBAW1@(-'
    src = u + t + i + l    # u 与 l 是固定字符串，t是你要翻译的字符串，i是之前的时间戳
    m2 = hashlib.md5()
    m2.update(src.encode('utf-8'))
    str_sent = m2.hexdigest()

    ''' 
        i:number
        from:AUTO
        to:AUTO
        smartresult:dict
        client:fanyideskweb
        salt:1515462554510
        sign:32ea4a33c063d174a069959a5df1a115
        doctype:json
        version:2.1
        keyfrom:fanyi.web
        action:FY_BY_REALTIME
        typoResult:false
    '''
    head = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Content-Length':'200',
        'Connection':'keep-alive',
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'fanyi.youdao.com',
        'Origin':'http://fanyi.youdao.com',
        'Referer':'http://fanyi.youdao.com/',
        'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest',
        # 'Cookie': 'YOUDAO_MOBILE_ACCESS_TYPE=1; OUTFOX_SEARCH_USER_ID=833904829@10.169.0.84; OUTFOX_SEARCH_USER_ID_NCOO=1846816080.1245883; fanyi-ad-id=39535; fanyi-ad-closed=1; JSESSIONID=aaaYuYbMKHEJQ7Hanizdw; ___rl__test__cookies=1515471316884'
    }
    head['Cookie'] = 'OUTFOX_SEARCH_USER_ID=833904829@10.169.0.84; OUTFOX_SEARCH_USER_ID_NCOO=1846816080.1245883;  ___rl__test__cookies='+str(time.time()*1000)
                     # '___rl__test__cookies=1515471316884'

    data = {
        'i': t,
        'from':'AUTO',
        'to':'AUTO',
        'smartresult':'dict',
        'client':'fanyideskweb',
        'salt':i,
        'sign':str_sent,
        'doctype':'json',
        'version':'2.1',
        'keyfrom':'fanyi.web',
        'action':'FY_BY_REALTIME',
        'typoResult':'false'
    }

    s = requests.session()
    # print data
    url = 'http://fanyi.youdao.com/translate_o?smartresult=dict&smartresult=rule'


    # # 这是代理IP
    # proxy = [{'http': '139.224.24.26:8888'}]  # {'http':'121.41.6.85:3128'},{'http':'116.214.32.51:8080'}，测试时可用，后来不能用
    # # 创建ProxyHandler
    # proxy_support = request.ProxyHandler(random.choice(proxy))  # 多个可用的代理时随机选择一个
    # # 创建Opener
    # opener = request.build_opener(proxy_support)
    #
    # # 添加请求头
    # opener.addheaders = head
    # # 用opener来执行
    # data = urllib.parse.urlencode(data).encode(encoding='UTF8')
    # response = opener.open(url, data)
    # # 读取相应信息并解码
    # html = response.read().decode("utf-8")

    # proxy_ip = '112.85.171.140:9999'
    # proxies = {
    #     # 'http': proxy_ip,
    #            'https':proxy_ip}
    # p = s.post(url,data= data,headers = head, proxies=proxies)
    p = s.post(url, data=data, headers=head)
    return p.text

def get_reuslt(repsonse):
    # 通过 json.loads 把返回的结果加载成 json 格式
    # try:
    result = json.loads(repsonse)
    return result['translateResult'][0][0]['tgt']


def read_text_src(text_src, delimiter):
    if isinstance(text_src, str):
        with open(text_src, 'r') as f:
            text_src = [line.split(delimiter) for line in f]
    elif not isinstance(text_src, list):
        raise TypeError('text_src should be list or str')
    return text_src

def main(file_path, batch_num=100):
    # print("本程序调用有道词典的API进行翻译，可达到以下效果：")
    # print("外文-->中文")
    # print("中文-->英文")
    # word = input('请输入你想要翻译的词或句：')
    dir = './data'

    train_src = os.path.join(dir, file_path)
    texts = read_text_src(train_src, delimiter='\t')
    with open(train_src+'_youdao', 'w') as f:
        for i in range(0, len(texts), batch_num):  #批量翻译
            text = texts[i:i+batch_num]
            text_batch = ''
            text_tag = []
            for t in text:
                f.write(t[0] + '\t' + t[1].strip() + '\n')
                # if t[0] != 'neu':
                #     continue
                text_batch += t[1]
                text_tag.append(t[0])
            print(text)

            if text_batch == '':
                continue
            #批量翻译
            #先翻译成英文
            list_trans = translate(text_batch)
            if list_trans is not None and json.loads(list_trans)['errorCode'] == 0:
                text_batch = ''
                for t in json.loads(list_trans)['translateResult']:
                    text_batch += t[0]['tgt'] + '\n'

                #英文--》中文
                chinese_trans = translate(text_batch.strip('\n'))
                if chinese_trans is not None:
                    ct = json.loads(chinese_trans)
                    if 'translateResult' in ct.keys():
                        for i, t in enumerate(json.loads(chinese_trans)['translateResult']):
                            print(t[0]['tgt'])
                            if t[0]['tgt'] is None:
                                continue
                            f.write(text_tag[i] + '\t' + t[0]['tgt'] + '\n')
            else:
                return False

            time.sleep(random.random() * 5)
if __name__ == '__main__':
    main('insurannce_train', batch_num=20)


