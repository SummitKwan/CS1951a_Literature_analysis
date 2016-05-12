import csv
import sys
import operator
from geopy.geocoders import Nominatim

city_radius = 0.3

def parse_locn(inst_string):
	comma_split = inst_string.split(',')
	split_len = len(comma_split)
	try:
		city = comma_split[split_len-2].strip()
		state = comma_split[split_len-1].strip()
		if not (city == '' or state == '') and len(state) == 2:
			return ', '.join([city.title(), state]).strip()
	except:
		return 'parse_locn_error'

def is_same_city(latLon1, latLon2):
	return abs(latLon1[0] - latLon2[0]) < city_radius and \
		abs(latLon1[1] - latLon2[1]) < city_radius

def updateLatLonList(lst, tpl):
	for i in range(len(lst)):
		locn = lst[i]
		if is_same_city((locn[0], locn[1]), (tpl[0], tpl[1])):
			lst[i] = (locn[0], locn[1], locn[2] + tpl[2], locn[3])
			print '\tJoining', tpl[3], 'with', locn[3]
			return

	lst.append(tpl)


def main(argv):
	inputFile = argv[0]
	outputFile = argv[1]

	# str location -> int count
	locns = {}
	num_locns = 150

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

	geolocator = Nominatim()

	# (lat, lon, count, str)
	latLonList = []	

	for i in range(num_locns):
		# try:
		locn_str = sorted_locns[i][0]
		count = sorted_locns[i][1]
		location = geolocator.geocode(locn_str)
		lat = location.latitude
		lon = location.longitude
		updateLatLonList(latLonList, (lat, lon, count, locn_str))

		# except:
		# 	print '\t', sorted_locns[i]
		# 	continue
	print 'here'
	with open(outputFile, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(['location', 'poster_count', 'latitude', 'longitude'])

		for i in range(len(latLonList)):
			locn = latLonList[i]
			lat = locn[0]
			lon = locn[1]
			count = locn[2]
			locn_str = locn[3]
			if (lon < -65 and lon > -125 and lat > 22 and lat < 50):
				writer.writerow([locn_str, count, lat, lon])
				print locn
			else:
				print '\t', locn


if __name__ == "__main__":
	main(sys.argv[1:])