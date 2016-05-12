import urllib
import lxml.html
import re
import sys

prefix = 'http://www.abstractsonline.com/Plan/'
abstracts_links = []

with open("page_source_" + sys.argv[1] + ".txt", 'r') as f:
	urls = re.findall(r'href=[\'"]?([^\'" >]+)', f.read())
	urls = [prefix + url for url in urls if url[0] == 'V']

outfile = open("abstract_urls_" + sys.argv[1] + ".txt", 'w+')

for my_url in urls:
	connection = urllib.urlopen(my_url)
	dom = lxml.html.fromstring(connection.read())
	for link in dom.xpath('//a/@href'): 
	    if link[:4] == 'View' and link not in my_url:
	    	abstracts_links.append(prefix + link)
	    	outfile.write(prefix + link)
	    	outfile.write('\n')

outfile.close()
