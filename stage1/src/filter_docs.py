#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-04 15:50:01
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import re
import os
import shutil

BAD_DOC_NUM_SET = set([13, 21, 58, 63, 71, 118, 160, 213, 254, 305, 307, 309, 322, 325, 345])
MARKED_DOC_DIR = '../marked_documents/'
FILTERED_DOC_DIR = '../filtered_documents/'

def is_bad_doc(doc_path):
    """Judge whether a document is 'bad'.
    A document is 'bad' if it is in blacklist or
    it contains less than 2 mentions of person names."""
    # print(doc_path)
    doc_num = int(doc_path.split('.')[0])
    if doc_num in BAD_DOC_NUM_SET:
        return True, 0
    person_name_num = 0
    doc = open(MARKED_DOC_DIR+doc_path, 'r')
    for line in doc.readlines()[2:]:
        person_names = re.findall('{.*?}', line)
        # print(' '.join(person_names))
        person_name_num +=  len(person_names)
    # return person_name_num == 0, person_name_num
    return False, person_name_num

if __name__ == '__main__':
    num_mentions = 0
    for doc_name in os.listdir(MARKED_DOC_DIR):

        if doc_name == '.DS_Store':
            continue
        bad_doc_flag, person_name_num = is_bad_doc(doc_name)

        if bad_doc_flag:
            print('Filtering out {}'.format(doc_name))
            try:
                os.remove(FILTERED_DOC_DIR+doc_name)
            except Exception as e:
                pass
        else:
            num_mentions += person_name_num
            shutil.copyfile(MARKED_DOC_DIR+doc_name, FILTERED_DOC_DIR+doc_name)
    
    print('After filtering, there are {} docs, {} mentions'
        .format(len(os.listdir(FILTERED_DOC_DIR)), num_mentions))

# {[^}]*?\.[^}]*?}