#!/usr/bin/env python
# coding: utf-8

# ## Import and Setup

# In[32]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-04 17:31:29
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import os
import pandas as pd
import numpy as np
import re
import timeit
import random
import nltk
import multiprocessing

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import precision_score, recall_score

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', -1)


# In[2]:


FILTERED_DOC_DIR = '../filtered_documents/'
MAX_EXAMPLE_LEN = 3
PREFIX_SUFFIX_LIST_DIR = '../prefix_suffix_lists/'
BLACK_WHITE_LIST_DIR = '../black_white_lists/'

FEATURE_LIST = [
    'contains_mex_char',
    'has_extras_in_middle',
    
    'next_word_verb',
    'all_proper_noun',
    
    'prefix_in_whitelist',
    'prefix_in_blacklist',
    'suffix_in_whitelist',
    'suffix_in_blacklist',
    
    'surrounded_by_paren',
    'has_left_comma',
    'has_right_comma',
    'has_left_period',
    'has_right_period',
    'first_last_word_capital',
    'surrounding_word_capital',
    'all_lowercase',

    'end_with_prime_s',
#     'tf',
#     'df',
#     'tf-idf'
]


# In[3]:


prefix_black_set, prefix_white_set = set(), set()
suffix_black_set, suffix_white_set = set(), set()

# intialize all black list and white list
for black_prefix in open(PREFIX_SUFFIX_LIST_DIR + 'prefix_black.txt', 'r').readlines():
    prefix_black_set.add(black_prefix.strip().lower())
for white_prefix in open(PREFIX_SUFFIX_LIST_DIR + 'prefix_white.txt', 'r').readlines():
    prefix_white_set.add(white_prefix.strip().lower())
for black_suffix in open(PREFIX_SUFFIX_LIST_DIR + 'suffix_black.txt', 'r').readlines():
    suffix_black_set.add(black_suffix.strip().lower())
for white_suffix in open(PREFIX_SUFFIX_LIST_DIR + 'suffix_white.txt', 'r').readlines():
    suffix_white_set.add(white_suffix.strip().lower())
    
prefix_suffix_set = set()
prefix_suffix_set = prefix_black_set | prefix_white_set | suffix_black_set | suffix_white_set

black_set = set()
for black_word in open(BLACK_WHITE_LIST_DIR + 'black_list.txt', 'r').readlines():
    black_set.add(black_word.strip().lower())


# ## Unil Functions

# In[4]:


def brackets_matching(example_padded, lbrace, rbrace):
    example_len = len(example_padded) - 4
    label = 0
    left_brace_max_index = -1
    for left_index in range(example_len-1, example_len+2):
        if lbrace in example_padded[left_index]:
            left_brace_max_index = left_index
    right_brace_min_index = len(example_padded)
    for right_index in range(4, 1, -1):
        if rbrace in example_padded[right_index]:
            right_brace_min_index = right_index
    if (left_brace_max_index > -1 and left_brace_max_index <= 2 and 
        right_brace_min_index < len(example_padded) and right_brace_min_index >= example_len+1):
        label = 1
    for left_index in range(example_len-1, example_len+1):
        if rbrace in example_padded[left_index] and left_index >= left_brace_max_index:
            label = 0
            break
    for right_index in range(4, 2, -1):
        if lbrace in example_padded[right_index] and right_index <= right_brace_min_index:
            label = 0
            break
    return label

def has_surrounded_symbol(example_padded, pos, symbol):
    example_len = len(example_padded) - 4
    if pos == 'left':
        if example_padded[1][-1] == symbol:
            return 1
        else:
            return 0
    else:
        if example_padded[example_len+1][-1] == symbol:
            return 1
        else:
            return 0

def remove_extras(s):
    if s in prefix_white_set or s in suffix_white_set:
        return s
    if s[-2:] == '\'s':
        s = s[:-2]
    s = re.sub('[^a-zA-Z]', '', s)
    return s

def gen_word_prop_dict(text):
    word_tag_dict = dict()
    words = nltk.word_tokenize(text)
    word_tags = nltk.pos_tag(words)
    for word, tag in word_tags:
        if word not in word_tag_dict:
            word_tag_dict[word] = set(tag)
        else:
            word_tag_dict[word].add(tag)
    return word_tag_dict


# In[5]:


label = brackets_matching(['father,', 'Dr.', '{Henry', 'Jones}.', 'The'], '{', '}')


# ## Feature and Label Definition

# In[6]:


# Generate feature matrix and label vector for a document and a particular example length
def gen_feature_label_example_len(text, example_len, word_tag_dict):
#     X_len = pd.DataFrame(columns=(['example'] + FEATURE_LIST))
    X_len = pd.DataFrame()
    y_len = pd.DataFrame(columns=['example', 'is_person_name'])
    parts = text.split(' ')
    index = 2
    while index+example_len+2 <= len(parts):
        example_padded = parts[index-2:index+example_len+2]
        example = example_padded[2:2 + example_len]
        example_joined = ' '.join(example)
        feature_dict = {'example': example_joined}
        
        # ========================================================================
        # "example_padded" has the following form:                              ||
        # [pad_0, pad_1, word_1, ..., word_n,                 pad_-2, pad_-1]   ||
        #  0      1      2            len-3 (example_len+1)   len-2   len-1     ||
        # ========================================================================
        
        # generate "surrounded_by_paren" feature
        feature_dict['surrounded_by_paren'] = brackets_matching(example_padded, '(', ')')

        # generate "has_left_comma" feature
        feature_dict['has_left_comma'] = has_surrounded_symbol(example_padded, 'left', ',')
        
        # generate "has_right_comma" feature
        feature_dict['has_right_comma'] = has_surrounded_symbol(example_padded, 'right', ',')
        
        # generate "has_left_period" feature
        feature_dict['has_left_period'] = has_surrounded_symbol(example_padded, 'left', '.')
        
        # generate "has_right_period" feature
        feature_dict['has_right_period'] = has_surrounded_symbol(example_padded, 'right', '.')
        
        # generate "all_lowercase" feature
        feature_dict['all_lowercase'] = 1 if re.fullmatch(r'[^A-Z]+', example_joined) else 0
        
        # generate "all_uppercase" feature
        feature_dict['all_uppercase'] = 1 if re.fullmatch(r'[^a-z]+', example_joined) else 0
        
        # generate "prefix_in_whitelist" feature
        feature_dict['prefix_in_whitelist'] = 1 if remove_extras(example_padded[1]) in prefix_white_set else 0
        
        # generate "prefix_in_blacklist" feature
        feature_dict['prefix_in_blacklist'] = 1 if (remove_extras(example_padded[1])).lower() in prefix_black_set else 0
        
        # generate "suffix_in_whitelist" feature
        feature_dict['suffix_in_whitelist'] = 1 if remove_extras(example_padded[2 + example_len]) in suffix_white_set else 0
        
        # generate "suffix_in_blacklist" feature
        feature_dict['suffix_in_blacklist'] = 1 if (remove_extras(example_padded[2 + example_len])).lower() in suffix_black_set else 0
        
        # generate "end_with_prime_s" feature
#         feature_dict['end_with_prime_s'] = 1 if (re.fullmatch('.*\'s', example_padded[1+example_len])) else 0
        
        # generate "first_last_word_capital" feature
        # TODO change to all_word_capotal
        first_capital = re.fullmatch('[^a-zA-Z]*[A-Z].*', example_padded[2])
        last_capital = re.fullmatch('[^a-zA-Z]*[A-Z].*', example_padded[1+example_len])
        feature_dict['first_last_word_capital'] = 1 if (first_capital and last_capital) else 0
        
        # generate "surrounding_word_capital" feature
#         left_capital = re.fullmatch('[^a-zA-Z]*[A-Z].*', example_padded[1])
#         right_capital = re.fullmatch('[^a-zA-Z]*[A-Z].*', example_padded[2+example_len])
#         feature_dict['surrounding_word_capital'] = 1 if (left_capital or right_capital) else 0
        
        # generate "next_word_verb" feautre, including be-verb
        feature_dict['next_word_verb'] = 0
        next_word = remove_extras(example_padded[2 + example_len])
        if next_word in word_tag_dict:
            for tag in word_tag_dict[next_word]:
                if tag.startswith('V'):
                    feature_dict['next_word_verb'] = 1
                    break

        # generate "all_noun" feautre
        feature_dict['all_noun'] = 1
        for word in example:
            word = remove_extras(word)
            if word not in word_tag_dict:
                feature_dict['all_noun'] = 0
                break
            can_be_noun = False
            for tag in word_tag_dict[word]:
                if tag.startswith('N'):
                    can_be_noun = True
                    break
            if not can_be_noun:
                feature_dict['all_noun'] = 0
                break
                    
        # generata "contains_proper_noun" feature
        feature_dict['contains_proper_noun'] = 0
        for word in example:
            word = remove_extras(word)
            if word in word_tag_dict and 'NNP' in word_tag_dict[word]:
                feature_dict['contains_proper_noun'] = 1
                break
        
        # generata "contains_extras_in_middle" feature
        feature_dict['contains_extras_in_middle'] = 0
        middle_chars = example_joined[2:-2]
        if re.search(r'[^a-zA-Z\s]', middle_chars):
            feature_dict['contains_extras_in_middle'] = 1
        
        # generata "contains_amazing_char" feature
        feature_dict['contains_amazing_char'] = 0 
        if re.search(r'[óéöäûâ]', example_joined):
            feature_dict['contains_amazing_char'] = 1
        
#         # generata "contains_prefix_suffix" feature
#         feature_dict['contains_prefix_suffix'] = 0
#         for word in example:
#             for some_fix in prefix_suffix_set:
#                 if some_fix in word:
#                     feature_dict['contains_prefix_suffix'] = 1
#                     break

        # generata "surrounding_word_and" feature
        feature_dict['surrounding_word_and'] = 0
        if example_padded[1] == 'and' or example_padded[-2] == 'and':
            feature_dict['surrounding_word_and'] = 1 
        
        # generate "in_blacklist" feature
        feature_dict['in_blacklist'] = 0
        for word in example:
            word = (remove_extras(word)).lower()
            if word in black_set or word in prefix_suffix_set:
                feature_dict['in_blacklist'] = 1
                break
        
        # generate "surrounding_black_word" feature
        feature_dict['surrounding_black_word'] = 0
        if example_padded[1] in black_set or example_padded[1] in prefix_suffix_set:
            feature_dict['surrounding_black_word'] = 1
        if example_padded[-2] in black_set or example_padded[-2] in prefix_suffix_set:
            feature_dict['surrounding_black_word'] = 1
        
        # generate "tf" feature
        
        # generate "idf" feature
        
        # generate "tf-idf" feature

        
        X_len = X_len.append(feature_dict, ignore_index=True)

        # generate label
        label = brackets_matching(example_padded, '{', '}')
        y_len = y_len.append({'example': example_joined, 'is_person_name': label}, ignore_index = True)

        index += 1

    return X_len, y_len

# Generate feature matrix and label vector for a document
def gen_feature_label_doc(doc_name):
#     X_doc = pd.DataFrame(columns=(['example'] + FEATURE_LIST))
    X_doc = pd.DataFrame()
    y_doc = pd.DataFrame(columns=['example', 'is_person_name'])
    doc = open(FILTERED_DOC_DIR+doc_name, 'r')
    text = ' '.join(doc.readlines()[2:]) # skip the title and empty line
    word_tag_dict = gen_word_prop_dict(text)
    
    text = '. . ' + text + ' . .' # pad with '. .' at both ends
    for example_len in range(1, MAX_EXAMPLE_LEN+1):
        X_len, y_len = gen_feature_label_example_len(text, example_len, word_tag_dict)
        X_doc = X_doc.append(X_len, ignore_index=True)
        y_doc = y_doc.append(y_len, ignore_index=True)
    return X_doc, y_doc

# Generate train/test feature matrix and label vector, given a list of documents
pool = multiprocessing.Pool(processes=10)
def gen_feature_label(doc_list):
    # X = pd.DataFrame()
    # y = pd.DataFrame(columns=['example', 'is_person_name'])
    
    feature_label_doc_list =  pool.map(gen_feature_label_doc, doc_list)
    feature_matrices, label_vectors = zip(*feature_label_doc_list)

    X = pd.concat(list(feature_matrices))
    y = pd.concat(list(label_vectors))

    # for doc_name in doc_list:
    #     if doc_name == '.DS_Store':
    #         continue
    #     X_doc, y_doc = gen_feature_label_doc(doc_name)
    #     X = X.append(X_doc, ignore_index=True)
    #     y = y.append(y_doc, ignore_index=True)
        
    return X, y


# ## Feature and Label Generation

# In[7]:


start = timeit.default_timer()

# documents are unordered
doc_list = os.listdir(FILTERED_DOC_DIR)

# documents are ordered
# doc_list = sorted(os.listdir(FILTERED_DOC_DIR), key = lambda x: int(x.split('.')[0]))

doc_list = doc_list[:5]

cutoff = int(0.66 * len(doc_list))

train_doc_list = doc_list[:cutoff]
test_doc_list = doc_list[cutoff:]

X_train, y_train = gen_feature_label(train_doc_list)
X_test, y_test = gen_feature_label(test_doc_list)
    
stop = timeit.default_timer()

print("Time used: ", stop - start)

# with pd.option_context('display.max_rows', None, 'display.max_columns', None):
#     print(X.head(1000), y.head(1000))
# X.head(1000)
# y.head(1000)


# In[9]:


X_train_no_example = X_train.drop(['example'], axis=1).astype('int')
X_test_no_example = X_test.drop(['example'], axis=1).astype('int')

y_train_no_example = y_train['is_person_name'].astype('int')
y_test_no_example = y_test['is_person_name'].astype('int')

clf = LogisticRegression(solver='lbfgs')
# clf = RandomForestClassifier()
clf.fit(X_train_no_example, y_train_no_example)

if isinstance(clf, LogisticRegression):
    coef_df = pd.DataFrame()
    coef_df['features'] = X_train_no_example.columns
    coef_df['coef'] = clf.coef_[0]
    print(coef_df)

y_predict = clf.predict(X_test_no_example)



precision = precision_score(y_test_no_example, y_predict)
recall = recall_score(y_test_no_example, y_predict)

print("Precision: {:.2f}%, Recall: {:.2f}%\n".format(precision*100, recall*100))

X_test[np.not_equal(y_test_no_example, y_predict)].head(100)

# print(X_test[np.not_equal(y_test_no_example, y_predict)])
# print(X_test[np.not_equal(y_test_no_example, y_predict)])

y_false = y_test[np.not_equal(y_test_no_example, y_predict)]
X_false = X_test[np.not_equal(y_test_no_example, y_predict)]
y_false['predicted_label'] = y_predict[np.not_equal(y_test_no_example, y_predict)]

print('=============================================')
print('Test False Positive: ')
print(y_false[y_false['predicted_label'] == 1])
# print(X_false[y_false['predicted_label'] == 1])

# print('=============================================')
# print('Test False Negative: ')
# print(y_compare[y_compare['predicted_label'] == 0])

y_predict_train = clf.predict(X_train_no_example)
y_false_train = y_train[np.not_equal(y_train_no_example, y_predict_train)]
y_false_train['predicted_label'] = y_predict_train[np.not_equal(y_train_no_example, y_predict_train)]

print('=============================================')
print('Train False Positive: ')
print(y_false_train[y_false_train['predicted_label'] == 1])

