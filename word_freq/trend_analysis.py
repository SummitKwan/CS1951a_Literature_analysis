import csv
import string
import json
import re

def tokenize(text):
    text = re.sub('[\.\,\/\\\&\=\:\;\"\(\)\[\]\{\}\?\!\$\*\%]','',text) 
    tokens = []
    for word in text.split():
        if word[0].isupper() and word[-1].islower():
            word = word.lower()
        tokens.append(word)
    return tokens

header = ['pres_title', 'location', 'pres_time', 'presenter_at', 'topic', 'authors', 'institute', 'abstract', 'disclosures', 'keywords']
years = ['2009','2010','2011','2012','2013','2014','2015']
itc = 7
dc = 2
all_words = {}
all_count = 0
ytw = {}
ytc = {}
for y in years:
	ytw[y] = {}
	ytc[y] = 0
with open('../aggregate_data.csv') as f:
	reader = csv.reader(f)
	row = reader.next()
	for row in reader:
		words = tokenize(row[itc])
		key = ''
		for y in years:
			if y in row[dc]:
				key = y
		if key == '': continue
		for w in words:
			if len(w) <= 2: continue
			all_count += 1
			ytc[key] += 1
			if w in all_words: all_words[w] += 1
			else: all_words[w] = 1
			hm = ytw[key]
			if w in hm: hm[w] += 1
			else: hm[w] = 1

wti = {}
for w in all_words:
	if all_words[w] <= 100: continue
	cnt_years = 0
	for y in years:
		if w in ytw[y]: cnt_years += 1
	if cnt_years < 2: continue
	wti[w] = {}
	wti[w]['total_freq'] = all_words[w]/float(all_count)
	for y in years:
		if w in ytw[y]: wti[w][y] = ytw[y][w]/float(ytc[y])
		else: wti[w][y] = 0.0

with open('results_100_2_years.json', 'w') as of2:
    json.dump(wti, of2)





