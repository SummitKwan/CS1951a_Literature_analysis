import csv
import operator
from sets import Set
import string

col_num_to_dict = {}

stop_words = Set(['', 'of', 'in', 'the', 'and', 'to', 'a', 'for', 'with', 'by',
				'that', 'we', 'is', 'were', 'was', 'are', 'these', 'or', 'an',
				'at', 'not', 'which', 'as', 'on', 'this', 'from', 'be', 'have',
				'during', 'our', 'has', 'been', 'can', 'it', 'also', 'but',
				'may', 'their', 'two', 'however', 'both', 'after', 'using',
				'found', 'used', 'et', 'al', 'than', 'while', 'when', 'suggest',
				'such', '1', '2', '3', 'showed', 'more', 'there', 'here', 'all',
				'within', 'well', 'its', 'whether', 'into'])

def clean_word(word):
	word = word.lower()

	exclude = set(string.punctuation)
	return ''.join(c for c in word if c not in exclude)

def inc_dict(dict, key):
	if key in dict:
		dict[key] = dict[key] + 1
	else:
		dict[key] = 1

def count_bigrams(sentence, dict):
	prev = ''
	i = 0
	for word in sentence.split(' '):
		word = clean_word(word)

		if not (word in stop_words and prev in stop_words) \
			and not (word == '' or prev == ''):
			inc_dict(dict, ' '.join([prev, word]))

		prev = word

	return dict

def count_words(sentence, dict):
	for word in sentence.split(' '):
		word = clean_word(word)
		if word in stop_words:
			continue
		inc_dict(dict, word)

	return dict

def init_dicts(col_num_list):
	for col_num in col_num_list:
		col_num_to_dict[col_num] = {}

cols_to_count = [0, 4, 6, 7, 9]
init_dicts(cols_to_count)

with open('abstract_data.csv', 'rb') as f:
	reader = csv.reader(f)
	next(reader)

	for row in reader:
		for col_num in cols_to_count:
			col_num_to_dict[col_num] = count_words(row[col_num], col_num_to_dict[col_num])
		

sorted_title = sorted(col_num_to_dict[0].items(), key=operator.itemgetter(1), reverse=True)
sorted_abstract = sorted(col_num_to_dict[7].items(), key=operator.itemgetter(1), reverse=True)
sorted_keywords = sorted(col_num_to_dict[9].items(), key=operator.itemgetter(1), reverse=True)
sorted_institutes = sorted(col_num_to_dict[6].items(), key=operator.itemgetter(1), reverse=True)
sorted_topics = sorted(col_num_to_dict[4].items(), key=operator.itemgetter(1), reverse=True)

with open('unigram_count.csv', 'wb') as f:
	writer = csv.writer(f)
	writer.writerow(['title', 'abstract', 'keywords', 'institute', 'topics'])
	for i in range(80):
		writer.writerow([sorted_title[i], sorted_abstract[i], sorted_keywords[i], 
			sorted_institutes[i], sorted_topics[i]])



print 'Title words'
for i in range(40):
	print sorted_title[i]

print

print 'Abstract words'
for i in range(40):
	print sorted_abstract[i]

print

print 'Keywords'
for i in range(40):
	print sorted_keywords[i]

print

print 'Institutes'
for i in range(40):
	print sorted_institutes[i]

print

print 'Topics'
for i in range(40):
	print sorted_topics[i]