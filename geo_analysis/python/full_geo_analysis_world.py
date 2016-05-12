import csv
import sys
import operator
from geopy.geocoders import Nominatim
import itertools

city_radius = 0.3

def parse_locn(inst_string):
	comma_split = inst_string.split(',')
	split_len = len(comma_split)
	try:
		city = comma_split[split_len-2].strip()
		state = comma_split[split_len-1].strip()
		if not (city == '' or state == ''):
			if len(state) == 2:
				return ', '.join([city.title(), state]).strip()
			elif state.lower() == 'canada':
				canada_city = comma_split[split_len-3].strip().title()
				return ', '.join([canada_city, city, state]).strip()
			else:
				return ', '.join([city.title(), state.title()]).strip()
	except:
		return 'parse_locn_error'

def is_same_city(latLon1, latLon2):
	return abs(latLon1[0] - latLon2[0]) < city_radius and \
		abs(latLon1[1] - latLon2[1]) < city_radius

def update_lat_lon_list(lst, tpl, town_to_city):
	for i in range(len(lst)):
		locn = lst[i]
		if is_same_city((locn[0], locn[1]), (tpl[0], tpl[1])):
			lst[i] = (locn[0], locn[1], locn[2] + tpl[2], locn[3])
			town_to_city[tpl[3]] = locn[3]
			print '\tJoining', tpl[3], 'with', locn[3]
			return

	lst.append(tpl)


def remove_asterisks(str_):
	return str_.translate(None, '*')

def update_pairs(locn_set, pair_counts, town_to_city):
	for city1, city2 in itertools.product(locn_set, locn_set):
		if city1 in town_to_city:
			city1 = town_to_city[city1]
		if city2 in town_to_city:
			city2 = town_to_city[city2]

		if city1 == city2:
			continue

		tmp1 = city1
		city1 = min(city1, city2)
		city2 = max(tmp1, city2)

		pair = (city1, city2)
		if pair in pair_counts:
			pair_counts[pair] += 1
		else:
			pair_counts[pair] = 1

def main(argv):
	input_file = argv[0]
	count_output_file = argv[1]
	arcs_output_file = argv[2]


	# str location -> int count
	locns = {}
	num_locns = 200
	num_arcs = 250

	# str location -> set(str author)
	auths_by_locn = {}

	# str author -> set(location)
	auth_to_locns = {}

	# all of the authors
	auths = set()

	# city to larger/containing city
	town_to_city = {}

	with open(input_file, 'rb') as f:
		reader = csv.reader(f)
		next(reader)

		for row in reader:
			inst_string = row[6]
			locn = parse_locn(inst_string)
			if locn == None:
				continue

			if locn in locns:
				locns[locn] += 1
			else:
				locns[locn] = 1

			author_str = remove_asterisks(row[5])
			curr_auth_lst = [s.strip() for s in author_str.split(',')]
			curr_auth_set = set(curr_auth_lst)
			auths.update(curr_auth_set)
			
			if locn in auths_by_locn:
				auths_by_locn[locn].update(curr_auth_set)
			else:
				auths_by_locn[locn] = curr_auth_set

			for auth in curr_auth_lst:
				if auth in auth_to_locns:
					auth_to_locns[auth].update(set([locn]))
				else:
					auth_to_locns[auth] = set([locn])


	

	sorted_locns = sorted(locns.items(), key=operator.itemgetter(1), reverse=True)

	geolocator = Nominatim()

	# (lat, lon, count, str)
	lat_lon_list = []

	# str locn -> (lat, lon)
	locn_lat_lon = {}

	for i in range(num_locns):
		try:
			locn_str = sorted_locns[i][0]
			count = sorted_locns[i][1]
			location = geolocator.geocode(locn_str)
			lat = location.latitude
			lon = location.longitude

			update_lat_lon_list(lat_lon_list, (lat, lon, count, locn_str), town_to_city)
			locn_lat_lon[locn_str] = (lat, lon)

		except:
			print '\t', sorted_locns[i]
			continue


	# (str locn, str locn) -> int count
	locn_pair_counts = {}
	for k, v in auth_to_locns.iteritems():
		update_pairs(v, locn_pair_counts, town_to_city)

	sorted_pair_counts = sorted(locn_pair_counts.items(), key=operator.itemgetter(1), \
		reverse=True)
	for tpl in sorted_pair_counts:
		print tpl
		print

	with open(count_output_file, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(['location', 'poster_count', 'latitude', 'longitude'])

		for i in range(len(lat_lon_list)):
			locn = lat_lon_list[i]
			lat = locn[0]
			lon = locn[1]
			count = locn[2]
			locn_str = locn[3]
			# if (lon < -65 and lon > -125 and lat > 22 and lat < 50):
			# 	writer.writerow([locn_str, count, lat, lon])
			# 	print locn
			# else:
			# 	print '\t', locn
			writer.writerow([locn_str, count, lat, lon])

	with open(arcs_output_file, 'wb') as f:
		writer = csv.writer(f)
		writer.writerow(['location1', 'lat1', 'lon1', 'location2', 'lat2', 'lon2', \
			'count'])
		for i in range(num_arcs):
			try:
				locn1 = sorted_pair_counts[i][0][0]
				locn2 = sorted_pair_counts[i][0][1]
				count = sorted_pair_counts[i][1]

				lat1 = locn_lat_lon[locn1][0]
				lon1 = locn_lat_lon[locn1][1]
				lat2 = locn_lat_lon[locn2][0]
				lon2 = locn_lat_lon[locn2][1]

				writer.writerow([locn1, lat1, lon1, locn2, lat2, lon2, count])
			except:
				continue

if __name__ == "__main__":
	main(sys.argv[1:])