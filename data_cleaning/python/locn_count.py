import csv
import sys
import operator

def parse_locn(inst_string):
	comma_split = inst_string.split(',')
	split_len = len(comma_split)
	try:
		return ','.join([comma_split[split_len-2], comma_split[split_len-1]]).strip()
	except:
		return 'parse_locn_error'

def main(argv):
	inputFile = argv[0]

	# str location -> int count
	locns = {}

	with open(inputFile, 'rb') as f:
		reader = csv.reader(f)
		next(reader)

		for row in reader:
			inst_string = row[6]
			locn = parse_locn(inst_string)

			if locn in locns:
				locns[locn] += 1
			else:
				locns[locn] = 1

	sorted_locns = sorted(locns.items(), key=operator.itemgetter(1), reverse=True)

	# print sorted_locns

	for i in range(40):
		print sorted_locns[i]

if __name__ == "__main__":
	main(sys.argv[1:])