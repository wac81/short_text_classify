from collections import defaultdict
import pickle
import os

import jieba
import jieba.analyse
import jieba.posseg as psg
import random
# from bert_serving.client import BertClient
from .base import *
import numpy as np
from copy import deepcopy

# bc = BertClient()


__all__ = ['GroceryTextConverter']

# print(jieba.analyse.extract_tags('请看图片中，一行代码没有修改，你是不是文件中"无法" 加了引号？？', 2))
def _dict2list(d):
    if len(d) == 0:
        return []
    m = max(v for k, v in d.items())
    ret = [''] * (m + 1)
    for k, v in d.items():
        ret[v] = k
    return ret


def _list2dict(l):
    return dict((v, k) for k, v in enumerate(l))

def del_punc(t):
    # t = t.replace('，', '')
    # t = t.replace('。', '')
    # t = t.replace('？', '')
    # t = t.replace('！', '')
    # t = t.replace('：', '')
    # t = t.replace(';', '')
    # t = t.replace('"', '')
    # t = t.replace('\'', '')
    #
    # t = t.replace('!', '')
    #
    # t = t.replace('?', '')
    # t = t.replace('!', '')
    # return t
    temp = ''
    for word, pos in psg.cut(t.strip()):
        if pos[0] != 'x':  #去除标点
            temp += word

    return temp


class GroceryTextPreProcessor(object):
    def __init__(self, stopwords_mode=False,
                 keywords_mode=True,#keywords default True
                 POS_mode=True,
                 bert_mode=False,
                 extend_mode=True):

        # index must start from 1
        self.tok2idx = {'>>dummy<<': 0}
        self.idx2tok = None
        self.keywords_mode = keywords_mode
        self.POS_mode = POS_mode
        self.bert_mode = bert_mode
        self.extend_mode = extend_mode

        if stopwords_mode:
            jieba.analyse.set_stop_words('stopwords.txt')

    @staticmethod
    def _default_tokenize(text):
        return jieba.cut(text.strip(), cut_all=True)

    @staticmethod
    def _default_get_keyword(text, topK=10):
        return jieba.analyse.extract_tags(text, topK)

    @staticmethod
    def _default_POS(text):
        return psg.cut(text.strip())


    def preprocess(self, text, custom_tokenize):
        # text = del_punc(text)  # 去除标点，和停用词区分开

        if custom_tokenize is not None:
            tokens = custom_tokenize(text)
        else:
            if self.POS_mode:
                tokens = self._default_POS(text)
                tokens = [word + pos[0] for word, pos in tokens]  #'去v'
                # tokens += [word for word, pos in tokens]
            else:
                tokens = self._default_tokenize(text)

        # if self.keywords_mode:
        #     if self.POS_mode:
        #         tokens = list(tokens)
        #         keywords = self._default_get_keyword(text)
        #         for i in range(3):    # 关键字模式 ， 默认将会把关键字重复1次
        #             for k in keywords:
        #                 for t in tokens:
        #                     if k in t:
        #                         tokens.append(t)
        #                         break
        #
        #     else:
        #         tokens = list(tokens)
        #         # for i in range(3):
        #         key = self._default_get_keyword(text)
        #         tokens += ['key' for k in key]


        ret = []
        for idx, tok in enumerate(tokens):
            if tok not in self.tok2idx:
                self.tok2idx[tok] = len(self.tok2idx)
            ret.append(self.tok2idx[tok])
        return ret

    def save(self, dest_file):
        self.idx2tok = _dict2list(self.tok2idx)
        config = {'idx2tok': self.idx2tok}
        pickle.dump(config, open(dest_file, 'wb'), -1)

    def load(self, src_file):
        config = pickle.load(open(src_file, 'rb'))
        self.idx2tok = config['idx2tok']
        self.tok2idx = _list2dict(self.idx2tok)
        return self


class GroceryFeatureGenerator(object):
    def __init__(self):
        self.ngram2fidx = {'>>dummy<<': 0}
        self.fidx2ngram = None

    def unigram(self, tokens):
        feat = defaultdict(int)
        NG = self.ngram2fidx
        for x in tokens:
            if (x,) not in NG:
                NG[x,] = len(NG)
            feat[NG[x,]] += 1
        return feat

    def bigram(self, tokens):
        feat = self.unigram(tokens)
        NG = self.ngram2fidx
        for x, y in zip(tokens[:-1], tokens[1:]):
            if (x, y) not in NG:
                NG[x, y] = len(NG)
            feat[NG[x, y]] += 1
        return feat

    def save(self, dest_file):
        self.fidx2ngram = _dict2list(self.ngram2fidx)
        config = {'fidx2ngram': self.fidx2ngram}
        pickle.dump(config, open(dest_file, 'wb'), -1)

    def load(self, src_file):
        config = pickle.load(open(src_file, 'rb'))
        self.fidx2ngram = config['fidx2ngram']
        self.ngram2fidx = _list2dict(self.fidx2ngram)
        return self



class GroceryClassMapping(object):
    def __init__(self):
        self.class2idx = {}
        self.idx2class = None

    def to_idx(self, class_name):
        if class_name in self.class2idx:
            return self.class2idx[class_name]

        m = len(self.class2idx)
        self.class2idx[class_name] = m
        return m

    def to_class_name(self, idx):
        if self.idx2class is None:
            self.idx2class = _dict2list(self.class2idx)
        if idx == -1:
            return "**not in training**"
        if idx >= len(self.idx2class):
            raise KeyError(
                'class idx ({0}) should be less than the number of classes ({0}).'.format(idx, len(self.idx2class)))
        return self.idx2class[idx]

    def save(self, dest_file):
        self.idx2class = _dict2list(self.class2idx)
        config = {'idx2class': self.idx2class}
        pickle.dump(config, open(dest_file, 'wb'), -1)

    def load(self, src_file):
        config = pickle.load(open(src_file, 'rb'))
        self.idx2class = config['idx2class']
        self.class2idx = _list2dict(self.idx2class)
        return self


class GroceryTextConverter(object):
    def __init__(self, custom_tokenize=None):
        self.text_prep = GroceryTextPreProcessor()
        self.feat_gen = GroceryFeatureGenerator()
        self.class_map = GroceryClassMapping()
        self.custom_tokenize = custom_tokenize

    def get_class_idx(self, class_name):
        return self.class_map.to_idx(class_name)

    def get_class_name(self, class_idx):
        return self.class_map.to_class_name(class_idx)

    def bert_transform(self, text):
        vec = bc.encode([text])

        return vec
    def to_svm(self, text, class_name=None):
        feat = self.feat_gen.unigram(self.text_prep.preprocess(text, self.custom_tokenize))
        feat_copy = deepcopy(feat)

        if self.text_prep.POS_mode:
            tokens = [t[:-1] for t in self.text_prep.tok2idx.keys()]
        else:
            tokens = self.text_prep.tok2idx.keys()

        offset_len = 0
        if self.text_prep.bert_mode:
            offset_len += 20000

            #bert
            text_vec = self.bert_transform(text)
            #del start and end
            # text_vec = text_vec[0][1:len(text)+1]
            text_vec = text_vec[0]

            # for i, vec in enumerate(text_vec):
            #     feat[i + offset_len] = vec       #固定最末尾添加句向量768

            for i, char in enumerate(text):
                if i < len(text_vec):
                    if char in tokens:
                        for k in self.text_prep.tok2idx.keys():
                            if char in k:      #对齐包含pos的char，并得到idx
                                idx = self.text_prep.tok2idx[k]
                                break

                        char_vec = text_vec[i]
                        char_vec = np.float16(np.mean(char_vec))
                        # char_vec = np.float16(np.sum(char_vec))

                        feat[idx+offset_len] = char_vec + feat_copy[idx]     # 加法更有效， 乘以字符本来的频率
                    elif i+1 < len(text_vec) and len(text) > i+1 and char+text[i+1] in self.text_prep.tok2idx.keys():
                        for k in self.text_prep.tok2idx.keys():
                            if char in k:  # 对齐包含pos的char，并得到idx
                                idx = self.text_prep.tok2idx[char + text[i + 1]]
                                break

                        char1_vec = text_vec[i]
                        char2_vec = text_vec[i+1]
                        char_vec = np.mean(char1_vec + char2_vec)
                        feat[idx+offset_len] = char_vec + feat_copy[idx]     # 加法更有效， 乘以字符本来的频率
                    else:
                        pass

        feat_plus = {}
        if self.text_prep.keywords_mode:
            offset_len += 20000

            keywords = self.text_prep._default_get_keyword(text)
            for k in keywords:
                for t in self.text_prep.tok2idx.keys():
                    if k in t:
                        idx = self.text_prep.tok2idx[t]
                        # if (feat[idx]==0):
                        #     print(t)
                        feat[idx] = feat_copy[idx] * 2   #keywords 改变本身的值
                            # np.log(feat_copy[idx])
                        # print(feat[idx])
                        break

        if self.text_prep.extend_mode:


            # 加入词顺序这种方式不行
            # offset_len += 20000
            # i = 0
            # for idx in list(feat_copy.keys()):
            #     i+=1
            #     feat[idx+offset_len] = i

            #加入词的log信息(复制)
            offset_len += 20000
            for idx in list(feat_copy.keys()):
                feat[idx+offset_len] = np.log(feat_copy[idx])


            # #加入词频率/句子中字数
            # offset_len += 20000
            # for idx in list(feat_copy.keys()):
            #     feat[idx + offset_len] = feat_copy[idx]/len(feat_copy.keys())
            #
            #     print(feat_copy[idx]/len(feat_copy.keys()))

        # print(offset_len)
        if class_name is None:
            return feat
        return feat, self.class_map.to_idx(class_name)



    def convert_text(self, text_src, delimiter, output=None):
        if not output:
            output = '%s.svm' % text_src
        text_src = read_text_src(text_src, delimiter)
        with open(output, 'w') as w:
            for line in text_src:
                try:
                    label_raw, text = line
                except ValueError:
                    continue

                # # 4:1的比例去掉words  数据扩展 小数据量可以做 每类超过100可以考虑不做，如果加需仔细考察
                # tokens = jieba.lcut(text)
                # if len(tokens) > 6:
                #     drop_words_len = len(tokens) / 6
                #     del_tokens = random.choices(tokens, k=int(drop_words_len))
                #     for del_t in del_tokens:
                #         if del_t in tokens:
                #             tokens.remove(del_t)
                #
                #     feat, label = self.to_svm(''.join(tokens), label_raw)
                #     w.write('%s %s\n' % (label, ''.join(' {0}:{1}'.format(f, feat[f]) for f in sorted(feat))))




                # 正常数据
                feat, label = self.to_svm(text.strip(), label_raw)
                w.write('%s %s\n' % (label, ''.join(' {0}:{1}'.format(f, feat[f]) for f in sorted(feat))))



    def save(self, dest_dir):
        config = {
            'text_prep': 'text_prep.config.pickle',
            'feat_gen': 'feat_gen.config.pickle',
            'class_map': 'class_map.config.pickle',
        }
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)
        self.text_prep.save(os.path.join(dest_dir, config['text_prep']))
        self.feat_gen.save(os.path.join(dest_dir, config['feat_gen']))
        self.class_map.save(os.path.join(dest_dir, config['class_map']))

    def load(self, src_dir):
        config = {
            'text_prep': 'text_prep.config.pickle',
            'feat_gen': 'feat_gen.config.pickle',
            'class_map': 'class_map.config.pickle',
        }
        self.text_prep.load(os.path.join(src_dir, config['text_prep']))
        self.feat_gen.load(os.path.join(src_dir, config['feat_gen']))
        self.class_map.load(os.path.join(src_dir, config['class_map']))
        return self
