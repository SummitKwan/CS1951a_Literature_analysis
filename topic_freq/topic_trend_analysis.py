import csv
import string
import json

header = ['pres_title', 'location', 'pres_time', 'presenter_at', 'topic', 'authors', 'institute', 'abstract', 'disclosures', 'keywords']
years = ['2013','2014','2015']
itc = 4
dc = 2
np = 0
ytt = {'full':{}, 'half':{}, 'small':{}}
for y in years: 
	for k in ytt: ytt[k][y] = {}
with open('../../aggregate_data.csv') as f:
	reader = csv.reader(f)
	row = reader.next()
	for row in reader:
		key = ''
		for y in years:
			if y in row[dc]:
				key = y
		if key == '': continue
		if key == '2014': np += 1
		topic = row[itc]
		full = topic[2:8]
		half = topic[2:6]
		small = topic[2]
		if full not in ytt['full'][key]: ytt['full'][key][full] = 1
		else: ytt['full'][key][full] += 1
		if half not in ytt['half'][key]: ytt['half'][key][half] = 1
		else: ytt['half'][key][half] += 1
		if small not in ytt['small'][key]: ytt['small'][key][small] = 1
		else: ytt['small'][key][small] += 1

with open('data_small.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in sorted(ytt['small']['2013']):
    	writer.writerow([float(ytt['small'][y][w]) for y in years])

with open('topic_small.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in sorted(ytt['small']['2013']):
    	writer.writerow([w])

with open('data_half.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in sorted(ytt['half']['2013']):
    	writer.writerow([float(ytt['half'][y].get(w,0)) for y in years])

with open('topic_half.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in sorted(ytt['half']['2013']):
    	writer.writerow([w])

#with open('data_full.csv', 'wb') as f:
#    writer = csv.writer(f)
#    for w in ytt['full']['2013']:
#    	writer.writerow([float(ytt['full'][y].get(w,0)) for y in years])

#with open('topic_full.csv', 'wb') as f:
#    writer = csv.writer(f)
#    for w in ytt['full']['2013']:
#    	writer.writerow([w])



