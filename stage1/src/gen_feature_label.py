#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-04 17:31:29
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import os

import pandas as pd

FILTERED_DOC_DIR = '../filtered_documents/'
MAX_EXAMPLE_LEN = 3
FEATURE_LIST = [
    'has_left_paren',
    'has_right_paren',
    'has_left_comma',
    'has_right_comma',
    'has_left_period',
    'has_right_period',
    'first_last_word_capital',
    'surrounding_word_capital',
    'all_lowercase',
    'prefix_in_whitelist',
    'prefix_in_blacklist',
    'suffix_in_whitelist',
    'suffix_in_blacklist',
    'end_with_prime_s',
    'tf',
    'df',
    'tf-idf'
]

def gen_feature_mat_example_len(text, example_len):
    example_list_len = list()
    X_len = pd.DataFrame(columns=FEATURE_LIST)
    y_len = pd.DataFrame(columns=['is_person_name'])

    parts = text.split(' ')
    index = 2

    while index+example_len+2 <= len(parts):
        feature_dict = dict()
        example_padded = parts[index-2:index+example_len+2]
        example_list_len.append(' '.join(example_padded[2:2+example_len]))

        # example_padded has the following form:
        #  0      1      2            len-3 (example_len+1)   len-2   len-1
        # [pad_0, pad_1, word_1, ..., word_n, pad_-2, pad_-1]

        # generate has_left_paren
        if '(' in example_padded[1] or '(' in example_padded[2]:
            feature_dict['has_left_paren'] = 1
        else:
            feature_dict['has_left_paren'] = 0

        X_len = X_len.append(feature_dict, ignore_index=True)

        # generate label
        label = 0
        
        left_brace_max_index = -1
        for left_index in range(example_len-1, example_len+2):
            if '{' in parts[left_index]:
                left_brace_max_index = left_index
        right_brace_min_index = len(example_padded)
        for right_index in range(4, 1, -1):
            if '}' in parts[right_index]:
                right_brace_min_index = right_index

        if (left_brace_max_index <= 2 and right_brace_min_index >= example_len+1):
            label = 1
        y_len = y_len.append({'is_person_name':label}, ignore_index=True)

        index += 1

    return example_list_len, X_len, y_len

def gen_feature_mat_doc(doc_name):
    example_list_doc = list()
    X_doc = pd.DataFrame(columns=FEATURE_LIST)
    y_doc = pd.DataFrame(columns=['is_person_name'])
    doc = open(FILTERED_DOC_DIR+doc_name, 'r')
    text = ' '.join(doc.readlines()[2:]) # skip the title and empty line
    text = '. . ' + text + ' . .' # pad with '. .' at both ends
    for example_len in range(1, MAX_EXAMPLE_LEN+1):
        example_list_len, X_len, y_len = gen_feature_mat_example_len(text, example_len)
        example_list_doc += example_list_len
        X_doc = X_doc.append(X_len, ignore_index=True)
        y_doc = y_doc.append(y_len, ignore_index=True)
    return example_list_doc, X_doc, y_doc

if __name__ == '__main__':
    doc_list = os.listdir(FILTERED_DOC_DIR)
    example_list = list()
    X = pd.DataFrame(columns=FEATURE_LIST)
    y = pd.DataFrame(columns=['is_person_name'])
    for doc_name in doc_list[0:1]:
        example_list_doc, X_doc, y_doc = gen_feature_mat_doc(doc_name)
        example_list += example_list_doc
        X = X.append(X_doc, ignore_index=True)
        y = y.append(y_doc, ignore_index=True)
    print(example_list, X, y)
