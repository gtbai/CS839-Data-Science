#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# @Date    : 2019-05-06 22:58:01
# @Author  : Bruce Bai (guangtong.bai@wisc.edu)

import sys, tty, termios
import argparse

TO_LABEL_PATH = 'pairs_to_label.csv'
TABLE1_PATH = 'imdb'
TABLE2_PATH = 'tmdb'
LABELED_PATH = 'labeled_pairs.csv'
CKPT_PATH = 'checkpoint'

class _Getch:
    def __call__(self):
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(3)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--resume', dest='resume', action='store_true', help='resume labeling from previous checkpoint')
    args = parser.parse_args()
    params = vars(args) # convert to ordinary dict

    to_label_lines = open(TO_LABEL_PATH, 'r').readlines()
    to_label_schema = to_label_lines[0]
    to_label_lines = to_label_lines[1:]

    table1_lines = open(TABLE1_PATH, 'r').readlines()
    table1_schema = to_label_lines[0]
    table1_lines = table1_lines[1:]

    table2_lines = open(TABLE2_PATH, 'r').readlines()[1:]

    getch = _Getch()

    try:
        ckpt_f = open(CKPT_PATH, 'r+')
    except: # if the ckeckpoint file does not exist, create it
        ckpt_f = open(CKPT_PATH, 'w')

    start_line_id = 0
    if params['resume']:
        labeled_f = open(LABELED_PATH, 'a')
        print("Resuming from previous checkpoint...")
        try:
            start_line_id = int(ckpt_f.readline()) + 1
        except:
            print("WARNING: No checkpoint has been saved before! Start from the beginning...")
    else:
        labeled_f = open(LABELED_PATH, 'w')

    labeled_f.write(to_label_schema.strip() + ',label\n')
    for line_id, to_label_line in enumerate(to_label_lines):

        if line_id < start_line_id:
            continue

        id1, id2 = [int(_id) for _id in to_label_line.split(',')]
        tuple1, tuple2 = table1_lines[id1], table2_lines[id2]

        print("==========Tuple 1==========")
        print(tuple1)
        print("==========Tuple 2==========")
        print(tuple2)
        print("===========================")
        print("Please press left arrow key (<-) for no-match and right arrow key (->) for match:\n")

        while True:
            ch = getch()
            if ch == '\x1b[D': # left arrow key (<-)
                match = False
                print("You confirmed it as a NO-MATCH!")
                break
            elif ch == '\x1b[C': # right arrow key (->)
                match = True
                print("You confirmed it as a MATCH!")
                break
            elif ch == 'qqq':
                print("Quiting the system")
                exit()
            else:
                print("Input is not recognized, please press left arrow key (<-) for NO-MATCH and right arrow key (->) for MATCH!")
        labeled_f.write(','.join([str(id1), str(id2), str(match)]) + '\n')
        labeled_f.flush()
        
        # save the checkpoint
        ckpt_f.seek(0)
        ckpt_f.truncate()
        ckpt_f.write(str(line_id))
        ckpt_f.flush()

