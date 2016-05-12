import csv
from sets import Set

topics = Set()

with open('abstract_data.csv', 'rb') as f:
	reader = csv.reader(f);
	next(reader)
	for row in reader:
		topic = row[4]
		if not topic in topics:
			topics.add(topic)


print len(topics)