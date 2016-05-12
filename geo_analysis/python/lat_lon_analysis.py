import csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def main():

	with open('../data/researchLocnsUS.csv', 'rb') as f:
		reader = csv.reader(f)
		next(reader)

		x = []
		y = []
		sizes = []

		for row in reader:
			lat = float(row[2])
			lon = float(row[3])
			poster_count = float(row[1])
			reln_count = float(row[4])

			ratio = reln_count


			x.append(poster_count)
			y.append(ratio)
			sizes.append(2)

		x = np.array(x)
		y = np.array(y)

		fit = np.polyfit(x, y, deg=1)


		plt.ylabel('Relation Count')
		plt.xlabel('Poster Count')
		plt.suptitle('Relation Count vs. Poster Count')
		plt.scatter(x, y, s=sizes, alpha=0.5)
		plt.plot(x, fit[0] * x + fit[1])
		plt.savefig('scatter_ratios.png')


if __name__ == '__main__':
	main()