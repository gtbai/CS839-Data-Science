#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-03-04 15:50:01
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import re
import os
import shutil

# maybe can spare 393, 194
BAD_DOC_NUM_SET = set([7, 9, 11, 13, 20, 21, 22, 27, 38, 42, 43, 50, 58, 60, 63, 71, 72, 92, 96, 104, 107, 108, 118, 145, 147, 148, 160, 173, 170, 174, 188, 189, 194, 199, 213, 214, 218, 222, 226, 252, 254, 260, 269, 271, 280, 305, 306, 307, 309, 322, 325, 327, 334, 338, 345, 353, 354, 362, 368, 369, 370, 371, 376, 379, 393])

MARKED_DOC_DIR = '../marked_documents/'
FILTERED_DOC_DIR = '../filtered_documents/'
SET_I_DIR = '../set_I/'
SET_J_DIR = '../set_J/'

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
        # print(' '.join(person_names))
        person_name_num +=  len(person_names)
    # return person_name_num == 0, person_name_num
    return False, person_name_num

if __name__ == '__main__':
    num_docs = 0
    num_mentions = 0

    for doc_name in os.listdir(MARKED_DOC_DIR):

        if not doc_name.endswith('.txt'):
            continue
        bad_doc_flag, person_name_num = is_bad_doc(doc_name)

        if bad_doc_flag:
            print('Filtering out {}'.format(doc_name))
            try:
                os.remove(FILTERED_DOC_DIR+doc_name)
            except Exception as e:
                pass
        else:
            num_docs += 1
            if num_docs > 300:
                break
            num_mentions += person_name_num
            dest_dir = SET_I_DIR if num_docs <= 200 else SET_J_DIR
            shutil.copyfile(MARKED_DOC_DIR+doc_name, dest_dir+doc_name)
            # shutil.copyfile(MARKED_DOC_DIR+doc_name, FILTERED_DOC_DIR+doc_name)

    
    print('After filtering, there are {} docs, {} mentions'
        .format(num_docs, num_mentions))

# {[^}]*?\.[^}]*?}
