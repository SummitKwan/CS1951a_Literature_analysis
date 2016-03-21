"""

aim: generate word could from abstract

Shaobo Guan, 2016-0318, FRI
"""

# import modules and declare variables
import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt

current_filepath = os.path.dirname(__file__)


# read data from csv file, into pandas Dataframe
data_filepath = os.path.join ( current_filepath, '../DATA/abstract_data.csv' )
with open(data_filepath) as datafile:
    data = pd.read_csv(datafile)

# count abstract word occurrence
if False:
    vect = CountVectorizer(ngram_range=(1, 2), stop_words='english', lowercase=True)
    wourd_count = vect.fit_transform(data.abstract[0:5])

# get Short symbol of topic from data.topics
data['topicS'] = data.topic.str.extract('^\+\+(\w).*')
l_topicS = sorted(data.topicS.unique());


# ############### create word cloud  ###############
all_text = '\n'.join(data.abstract)  # join all abstract together
cloud = WordCloud(width=1024, height=768, ranks_only=True, background_color='white').generate(all_text)  # generate world could

name_file = os.path.join ( current_filepath, 'word_cloud_'+'all'+'.png' )
cloud.to_file(name_file)

text_topicS = dict();
# for every topic:
for topicS in l_topicS:
    if topicS is not np.nan:
        text_topicS[topicS] = '\n'.join(data.abstract[data.topicS==topicS])
        cloud_cur = WordCloud(width=1024, height=768, ranks_only=True, background_color='white').generate(text_topicS[topicS])
        name_file = os.path.join ( current_filepath, 'word_cloud_topic_'+topicS+'.png' )
        cloud_cur.to_file(name_file)

plt.figure()
plt.imshow(wordcloud)
plt.axis("off")


print ('finish')
