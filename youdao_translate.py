import json

import requests
import os

# 翻译函数，word 需要翻译的内容
def translate(word):
    # 有道词典 api
    url = 'http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule&smartresult=ugc&sessionFrom=null'
    # 传输的参数，其中 i 为需要翻译的内容
    key = {
        'type': "AUTO",
        'i': word,
        "doctype": "json",
        "version": "2.1",
        "keyfrom": "fanyi.web",
        "ue": "UTF-8",
        "action": "FY_BY_CLICKBUTTON",
        "typoResult": "false"
    }
    # key 这个字典为发送给有道词典服务器的内容
    response = requests.post(url, data=key)
    # 判断服务器是否相应成功
    if response.status_code == 200:
        # 然后相应的结果
        return response.text
    else:
        print("有道词典调用失败")
        # 相应失败就返回空
        return None

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


def main():
    # print("本程序调用有道词典的API进行翻译，可达到以下效果：")
    # print("外文-->中文")
    # print("中文-->英文")
    # word = input('请输入你想要翻译的词或句：')
    dir = './data'

    train_src = os.path.join(dir, 'train_src')
    texts = read_text_src(train_src, delimiter='\t')
    with open(train_src+'_modify', 'w') as f:
        for t in texts:
            text = t[1].strip()
            f.write(t[0] + '\t' + t[1].strip() + '\n')
            print(text)
            list_trans = translate(text)
            if list_trans != None:
                english = get_reuslt(list_trans)
                chinese_trans = translate(english)
                if chinese_trans != None:
                    chinese = get_reuslt(chinese_trans)
                    print(chinese)
                    f.write(t[0] + '\t' + chinese + '\n')





if __name__ == '__main__':
    main()