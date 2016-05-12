import json
import sys
import math
import csv

years = ['2009','2010','2011','2012','2013','2014','2015']
tf = 'total_freq'
with open(sys.argv[1]) as json_data:
    hm = json.load(json_data)

with open('data.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in hm:
    	writer.writerow([float(hm[w][y]) for y in years])

with open('titles.csv', 'wb') as f:
    writer = csv.writer(f)
    for w in hm:
    	writer.writerow([w])

