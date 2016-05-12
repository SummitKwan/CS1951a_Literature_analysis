import csv

def main():
	file_path_list = []
	for year in range(2009, 2016):
		file_path_list.append('./data/abstract_data_' + `year` + '.csv')

	out_hdr = ['pres_title', 'location', 'pres_time', 'presenter_at', \
	    	'topic', 'authors', 'institute', 'abstract', 'disclosures', \
	    	'keywords']

	num_cols = len(out_hdr)
	hdr_indices = {}
	for i in range(num_cols):
		hdr_indices[out_hdr[i]] = i

	with open('./data/aggregate_data.csv', 'wb') as out_f:
		writer = csv.writer(out_f)
		writer.writerow(out_hdr)

		for path in file_path_list:
			with open(path, 'rb') as f:
				reader = csv.reader(f)
				curr_hdr = reader.next()
				row_out = [''] * num_cols
				for row in reader:
					for i in range(len(curr_hdr)):
						row_out[hdr_indices[curr_hdr[i]]] = row[i]
					writer.writerow(row_out)

if __name__ == '__main__':
	main()