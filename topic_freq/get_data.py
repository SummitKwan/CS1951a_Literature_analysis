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
f = open('../../aggregate_data.csv')
f2 = open('small_data.csv', 'wb')
writer = csv.writer(f2)
reader = csv.reader(f)
row = reader.next()
writer.writerow(row)
for row in reader:
	key = ''
	for y in years:
		if y in row[dc]:
			key = y
	if key != '':
		writer.writerow(row)
f.close()
f2.close()