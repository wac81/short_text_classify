

# from learner_impl import *
from stclassify.classifier import *

from stclassify.text_process import *
# from bert_serving.client import BertClient




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
dir = './data'

# train_src = os.path.join(dir, 'train_amber')
# test_src = os.path.join(dir, 'test_amber')

train_src = os.path.join(dir, 'insurance_train')
test_src = os.path.join(dir, 'insurance_test')

# train_src = os.path.join(dir, 'train_chs')
# test_src = os.path.join(dir, 'test_chs')


# train_src = os.path.join(dir, 'train_src_youdao')
# test_src = os.path.join(dir, 'test_src')



'''
data expansion
'''
# from data_expansion import data_expansion
# lines = []
# with open(train_src, mode='r') as file:
#     lines_train = file.readlines()
#
# with open(test_src, mode='r') as file:
#     lines_test = file.readlines()
#
# train_src = train_src + '_exp'
# test_src = test_src + '_exp'
#
# with open(train_src, mode='w') as file:
#     for line in lines_train:
#         line = line.split('\t')
#         # file.write(line[0] + '\t' + line[1].strip() + '\n')
#         for sent in data_expansion(line[1].strip(), num_aug=2):
#             file.write(line[0] + '\t' + sent + '\n')
#
# with open(test_src, mode='w') as file:
#     for line in lines_test:
#         line = line.split('\t')
#         # file.write(line[0] + '\t' + line[1].strip() + '\n')
#         for sent in data_expansion(line[1].strip(), num_aug=2):
#             file.write(line[0] + '\t' + sent + '\n')





text_converter = GroceryTextConverter(custom_tokenize=custom_tokenize)
train_svm_file = '%s_train.svm' % name
#
#
# text_converter.convert_text(train_src, output=train_svm_file, delimiter='    ')
text_converter.set_text_parameters(
                                    # keywords_mode=True,
                                    POS_mode=True,
                                    # extend_new_text=True,
                                    # ngram_extend_mode=True
                                    )


text_converter.convert_text(train_src, output=train_svm_file, delimiter='\t')


'''
-s 4   多分类 大数据量  
               accuracy       recall         
neg            76.76%         79.43%         
pos            94.07%         95.86%         
neu            59.28%         41.95%         

0.9003548479907931
0.9005466577155462
-N 1 -T 0 , '-s 4 -c 1.'  extend enabled

-s 5 -c 1.1  小数据量最好,加数据扩展最好

'''
model = train(train_svm_file, '-N 1 -T 0', '-s 4 -c 1.')  #4, 5
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



# test_src = preprocess_data('./text_feature_extract/data/eye_shadow/')
test_result = GroceryTest(model).test(text_src=test_src,delimiter='\t')
# test_result = GroceryTest(model).test(text_src=test_src,delimiter='\t')

print(test_result.accuracy_labels)
print(test_result.recall_labels)
test_result.show_result()
print(test_result)