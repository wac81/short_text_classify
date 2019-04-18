

from text_process import *

from learner_impl import *
from classifier import *

custom_tokenize = None
train_svm_file = None
delimiter='\t'
name = 'test_model'
# train_src = [
#     ('education', '名师指导托福语法技巧：名词的复数形式'),
#     ('education', '中国高考成绩海外认可 是“狼来了”吗？'),
#     ('sports', '图文：法网孟菲尔斯苦战进16强 孟菲尔斯怒吼'),
#     ('sports', '四川丹棱举行全国长距登山挑战赛 近万人参与')
# ]

train_src = 'train.txt'

def preprocess_data(path):
    neg_path = os.path.join(path, 'neg.txt')
    neu_path = os.path.join(path, 'neu.txt')
    pos_path = os.path.join(path, 'pos.txt')

    sentences = []
    y_true = []

    texts = []
    with open(neg_path, 'r') as f:
        temp = f.readlines()
        temp = list(set(temp))
        sentences += temp
        for s in temp:
            texts.append(('neg', s.strip()))
        # y_true += [[1.0, 0.0, 0.0] for x in range(len(temp))]
        # np.full((0, len(temp)), 0)
        print ('load neg...')

    with open(neu_path, 'r') as f:
        temp = f.readlines()
        temp = list(set(temp))
        sentences += temp
        for s in temp:
            texts.append(('neu', s.strip()))
        print ('load neu...')

    with open(pos_path, 'r') as f:
        temp = f.readlines()
        temp = list(set(temp))
        sentences += temp
        for s in temp:
            texts.append(('pos', s.strip()))
        print ('load pos...')


    return texts

train_src = preprocess_data('./text_feature_extract/data/train_corpus/')


text_converter = GroceryTextConverter(custom_tokenize=custom_tokenize)
train_svm_file = '%s_train.svm' % name

# text_converter.convert_text(train_src, output=train_svm_file, delimiter='    ')
text_converter.convert_text(train_src, output=train_svm_file, delimiter='\t')

model = train(train_svm_file, '', '-s 1')
model = GroceryTextModel(text_converter, model)
model.save('sentiment', force=True)



def load(name):
    text_converter = GroceryTextConverter()
    model = GroceryTextModel(text_converter)
    model.load(name)
    return model

model = load('sentiment')

# model = load('test')

single_text = '中国高考成绩海外认可 是“狼来了”吗'

# r = model.predict_text(single_text)
# print(r)



test_src = preprocess_data('./text_feature_extract/data/eye_shadow/')
# test_result = GroceryTest(model).test(text_src='test.txt',delimiter='    ')
test_result = GroceryTest(model).test(text_src=test_src,delimiter='\t')

print(test_result.accuracy_labels)
print(test_result.recall_labels)
test_result.show_result()