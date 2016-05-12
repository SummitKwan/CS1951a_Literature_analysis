import requests
import re
import argparse
import csv

############## Utility Methods ##############

def filter_substring(whole_string, substring):
	return whole_string.replace(substring, '')

# Filters tags and their contents out of a string
def filter_whole_tags(string):
	TAG_RE = re.compile(r'<[^>]+>[^<]+<\/[^>]+>')

	return TAG_RE.sub('', string)

# Filters just tags out of a string
def filter_tags(string):
	LEFT_TAG_RE = re.compile(r'<[^>]+>')
	RIGHT_TAG_RE = re.compile(r'<\/[^>]+>')

	to_return = LEFT_TAG_RE.sub('', string)
	to_return = RIGHT_TAG_RE.sub('', to_return)

	return to_return

def filter_sups(string):
	TAG_RE = re.compile(r'<sup>[^<]+<\/sup>')	

	return TAG_RE.sub('', string)

# Filters ampersand stuff
def filter_amps(string):
	AMPS_RE = re.compile(r'&[^;]{0,5};')

	return AMPS_RE.sub('', string)

#############################################


############# Cleaning Methods ##############

def get_institute(raw_string):
	inst_split = raw_string.split(';')
	if len(inst_split) > 1:
		inst = inst_split[1]
	else:
		inst = ' '

	return filter_tags(filter_whole_tags(inst))

def get_authors(raw_string):
	authors_split = raw_string.split(';')[0]

	to_return = filter_sups(authors_split)
	to_return = filter_tags(to_return)

	return to_return

def get_disclosures(raw_string):
	to_return = filter_tags(raw_string)
	# to_return = filter_substring(to_return, 'None.')
	to_return = to_return.replace('None.', 'none, ')

	return to_return

def get_keywords(key_str_list):
	keywords = []
	for i in range(9, len(key_str_list)):
		keywords.append(key_str_list[i].strip())

	return ', '.join(keywords)

#############################################



def gen_row(key_str_list):
	row = []

	# Presentation Title / pres_title
	row.append(key_str_list[1])

	# Location / location
	row.append(key_str_list[2])

	# Presentation Time / pres_time
	row.append(key_str_list[3])

	# Presenter At Poster Time / presenter_at
	row.append(key_str_list[4])

	# Topic / topic
	row.append(key_str_list[5])

	# Authors / authors
	row.append(get_authors(key_str_list[6]))

	# Institute / institute
	row.append(get_institute(key_str_list[6]))

	# Abstract / abstract
	row.append(filter_tags(key_str_list[7]))

	# Disclosures / disclosures
	row.append(get_disclosures(key_str_list[8]))

	# Keywords / keywords
	row.append(get_keywords(key_str_list))


	return row



def get_key_str_list(url):
	page = requests.get(url)
	my_str =  ' '.join(page.content.split('\n'))
	my_str = filter_amps(my_str)
	my_list = re.findall(r"<tr>(.*?)</tr>", my_str)
	my_list = [elt for elt in my_list if 'ViewAbstractDataLabel' in elt]
	if len(my_list) == 0: exit()
	key_str = my_list[0]
	key_str = key_str.replace('\r', ' ')
	key_str = key_str.split('> Support:</td>')[0]
	key_str_list = key_str.split('ViewAbstractDataLabel')
	key_str_list_list = [elt.split('width') for elt in key_str_list]
	key_str_list = [elt[2] for elt in key_str_list_list if len(elt) > 2]
	key_str_list = [elt[8:] for elt in key_str_list]
	key_str_list = [elt[:elt.find('</td>')] for elt in key_str_list]

	return key_str_list


def main(input_file, output_file):
	with open(output_file, 'wb') as f:
	    writer = csv.writer(f)
	    writer.writerow(['pres_title', 'location', 'pres_time', 'presenter_at', \
	    	'topic', 'authors', 'institute', 'abstract', 'disclosures', \
	    	'keywords'])

	    data = []

	    num_to_parse = 40000

	    with open(input_file, 'rb') as urls:
	    	i = num_to_parse
	    	for url in urls:
				if i < 1:
					break
				try:		
					data.append(gen_row(get_key_str_list(url)))
				except:
					continue
				i -= 1
				print "Doomsday countdown", i

	    # for i in range(num_to_parse):
	    #     writer.writerow(data[i])
	    for row in data:
	    	writer.writerow(row)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('input_file')
	parser.add_argument('output_file')
	args = parser.parse_args()
	main(args.input_file, args.output_file)