import os
import pandas as pd
import re

FILTERED_DOC_DIR = '../filtered_documents/'
MAX_EXAMPLE_LEN = 3
doc_list = os.listdir(FILTERED_DOC_DIR)

def remove_extras(s):
	if s[-2:] == '\'s':
		s = s[:-2]
	s = re.sub('[^a-zA-Z\.]', '', s)
	return s

def possible_black_generation(text):
	parts = text.split(' ')
	black_set = set()
	for index in range(2, len(parts) - 2):
		if ('{' in parts[index - 2]) or ('{' in parts[index - 1]) or ('{' in parts[index]):
			continue
		if ('}' in parts[index]) or ('}' in parts[index + 1]) or ('}' in parts[index + 2]):
			continue
		if re.fullmatch('[A-Z].*', parts[index]):
			black_set.add(remove_extras(parts[index]))
	return black_set



black_set = set()
for doc_name in doc_list:
	doc = open(FILTERED_DOC_DIR+doc_name, 'r')
	text = ' '.join(doc.readlines()[2:])
	text = '. . ' + text + ' . .' # pad with '. .' at both ends
	black_set = black_set | possible_black_generation(text)
for s in black_set:
	print(s)
	