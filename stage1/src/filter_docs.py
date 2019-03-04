#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-04 15:50:01
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import re
import os
import shutil

BAD_DOC_NUM_SET = set([58, 63, 71, 118, 213, 307, 345])
MARKED_DOC_DIR = '../marked_documents/'
FILTERED_DOC_DIR = '../filtered_documents/'

def is_bad_doc(doc_path):
    """Judge whether a document is 'bad'.
    A document is 'bad' if it is in blacklist or
    it contains less than 2 mentions of person names."""
    print(doc_path)
    doc_num = int(doc_path.split('.')[0])
    if doc_num in BAD_DOC_NUM_SET:
        return True, 0
    person_name_num = 0
    doc = open(MARKED_DOC_DIR+doc_path, 'r')
    for line in doc.readlines()[2:]:
        person_names = re.findall('{.*?}', line)
        print(' '.join(person_names))
        person_name_num +=  len(person_names)
    # return person_name_num < 2, person_name_num
    return False, person_name_num

if __name__ == '__main__':
    num_mentions = 0
    for doc_path in os.listdir(MARKED_DOC_DIR):
        if doc_path == '.DS_Store':
            continue
        bad_doc_flag, person_name_num = is_bad_doc(doc_path)
        if not bad_doc_flag:
            num_mentions += person_name_num
            shutil.copyfile(MARKED_DOC_DIR+doc_path, FILTERED_DOC_DIR+doc_path)
    print('Total number of mentions', num_mentions)