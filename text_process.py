from collections import defaultdict
import pickle
import os

import jieba
import jieba.analyse
import jieba.posseg as psg
import random


from base import *

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
    t = t.replace('，', '')
    t = t.replace('。', '')
    t = t.replace('？', '')
    t = t.replace('！', '')
    t = t.replace('：', '')
    t = t.replace(';', '')
    t = t.replace('"', '')
    t = t.replace('\'', '')

    t = t.replace('!', '')

    t = t.replace('?', '')
    t = t.replace('!', '')
    return t

class GroceryTextPreProcessor(object):
    def __init__(self, stopwords_mode=False,
                 keywords_mode=False,#keywords default True
                 POS_mode=True):
        # index must start from 1
        self.tok2idx = {'>>dummy<<': 0}
        self.idx2tok = None
        self.keywords_mode = keywords_mode
        self.POS_mode = POS_mode
        if stopwords_mode:
            jieba.analyse.set_stop_words('stopwords.txt')

    @staticmethod
    def _default_tokenize(text):
        return jieba.cut(text.strip(), cut_all=True)

    @staticmethod
    def _default_get_keyword(text, topK=3):
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
                temp_word = []
                temp_pos = []
                for word, pos in tokens:
                    temp_word.append(word+pos[0])
                    # temp_word.append(word)
                    # temp_pos.append(pos[0])
                # tokens = temp_word + temp_pos
                tokens = temp_word

            else:
                tokens = self._default_tokenize(text)

        if self.keywords_mode:
            if self.POS_mode:
                tokens = list(tokens)
                keywords = self._default_get_keyword(text)
                for i in range(3):    # 关键字模式 ， 默认将会把关键字重复1次
                    for k in keywords:
                        for t in tokens:
                            if k in t:
                                tokens.append(t)
                                break

            else:
                tokens = list(tokens)
                for i in range(1):
                    tokens += self._default_get_keyword(text)

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

    def to_svm(self, text, class_name=None):
        feat = self.feat_gen.bigram(self.text_prep.preprocess(text, self.custom_tokenize))

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
