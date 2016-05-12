from __future__ import division
import sys
import csv
import argparse
from collections import defaultdict

import util
import random

import numpy
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, confusion_matrix
from sklearn import cross_validation
from sklearn.naive_bayes import BernoulliNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from tokenizer import Tokenizer

# command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--classifier', default='nb', help='nb | log | svm')
parser.add_argument('-f', '--field', default='title', help='title or abstract')
parser.add_argument('-test', help='Tests with this item')

opts = parser.parse_args()

# variables
train_number = 20000
topic_index = 4
feature_index = 7
if opts.field == 'title': feature_index = 0
label_space = {'A':1, 'B':2, 'C':3, 'D':4, 'E':5, 'F':6, 'G':7, 'H':8}

all_x_y = []

# get the data
with open('data/abstract_data_raw.csv', 'rb') as csvfile:
	reader = csv.reader(csvfile)
	reader.next()
	counter = 0
	for row in reader:
		if row[topic_index][2] not in label_space: continue
		y = label_space[row[topic_index][2]]
		x = row[feature_index]
		all_x_y.append((x,y))

# randomize
random.shuffle(all_x_y);

# split into train and test
train_x_y = all_x_y[:train_number]
test_x_y = all_x_y[train_number:]

# extract texts and labels
training_texts = [item[0] for item in train_x_y]
training_labels = [item[1] for item in train_x_y]

print '========== Training ==========='

# instantiate tokenizer and vectorizer
tokenizer = Tokenizer()
vectorizer = CountVectorizer(binary=False, lowercase=True, decode_error='replace', tokenizer=tokenizer)

# get training features using vectorizer
training_features = vectorizer.fit_transform(training_texts)

# get training labels with numpy array
training_labels = numpy.array(training_labels)

##### TRAIN THE MODEL ######################################
# Initialize the corresponding type of the classifier and train it (using 'fit')
if opts.classifier == 'nb':
	# TODO: Initialize Naive Bayes and train
	classifier = BernoulliNB(binarize=None)
	classifier.fit(training_features, training_labels)
elif opts.classifier == 'log':
	# TODO: Initialize Logistic Regression and train
	classifier = LogisticRegression()
	classifier.fit(training_features, training_labels)
elif opts.classifier == 'svm':
	# TODO: Initialize SVM and train
	classifier = LinearSVC()
	classifier.fit(training_features, training_labels)
else:
	raise Exception('Unrecognized classifier!')
############################################################

# look at the train error from corss validation
scores = cross_validation.cross_val_score(classifier, training_features, training_labels, scoring='accuracy', cv=10)
print 'Cross Validation Mean Score: ', scores.mean()
print 'Cross Validation Standard Deviation: ', scores.std()

print '\n========== Most Informative Features ===========\n'
util.print_most_informative_features(opts.classifier, vectorizer, classifier, n=10)

print '\n========== Testing ===========\n'

if opts.test is not None:

	# TODO: Print the predicted label of the test tweet
	test_tweet_features = vectorizer.transform([opts.test])

	# TODO: Print the predicted probability of each label.
	if opts.classifier != 'svm': 
		# Use predict_proba
		print classifier.predict_proba(test_tweet_features)
	else: 
		# Use decision_funcion
		print classifier.decision_funcion(test_tweet_features)

else:
	# extract texts and labels
	test_texts = [item[0] for item in test_x_y]
	test_labels = [item[1] for item in test_x_y]

	# Get test features using vectorizer
	test_features = vectorizer.transform(test_texts)

	# Transform test labels to numpy array (numpy.array)
	test_labels = numpy.array(test_labels)

	predicted = classifier.predict(test_features)
	print confusion_matrix(test_labels, predicted)

	test_scores = classifier.score(test_features, test_labels)
	print 'Mean Score: ', test_scores.mean()

	############################################################