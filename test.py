

from text_process import *

from learner_impl import *
from classifier import *

custom_tokenize = None
train_svm_file = None
delimiter='\t'
name = 'test_model'
train_src = [
    ('education', '名师指导托福语法技巧：名词的复数形式'),
    ('education', '中国高考成绩海外认可 是“狼来了”吗？'),
    ('sports', '图文：法网孟菲尔斯苦战进16强 孟菲尔斯怒吼'),
    ('sports', '四川丹棱举行全国长距登山挑战赛 近万人参与')
]
text_converter = GroceryTextConverter(custom_tokenize=custom_tokenize)
train_svm_file = '%s_train.svm' % name

text_converter.convert_text(train_src, output=train_svm_file, delimiter=delimiter)

model = train(train_svm_file, '', '-s 4')
model = GroceryTextModel(text_converter, model)




single_text = 'CBA半决赛辽宁再负新疆总分0-2 WNBA纽约14顺位选中韩旭'

r = model.predict_text(single_text)
print(r)