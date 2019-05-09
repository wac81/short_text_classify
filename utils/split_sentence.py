import os, random


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
# train_src = preprocess_data('./text_feature_extract/data/train_corpus/')


def read_text_src(text_src, delimiter):
    if isinstance(text_src, str):
        with open(text_src, 'r') as f:
            text_src = [line.split(delimiter) for line in f]
    elif not isinstance(text_src, list):
        raise TypeError('text_src should be list or str')
    return text_src


def split_train_test(p, l):
    a = []
    b = []
    for x in l:
        if random.random() <= p:
            a.append(x)
        else:
            b.append(x)
    return a, b


train_src = 'chs_sentences.txt'

sentences = read_text_src(train_src,  delimiter='    ')

p = 0.5

train_src, test_src = split_train_test(p, sentences)
with open('train_chs', 'w') as w:
    for line in train_src:
        w.write(line[0]+'\t'+line[1].strip()+'\n')

with open('test_chs', 'w') as w:
    for line in test_src:
        w.write(line[0]+'\t'+line[1].strip()+'\n')

