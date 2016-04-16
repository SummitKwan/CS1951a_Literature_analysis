"""

aim: generate word could from abstract

Shaobo Guan, 2016-0318, FRI
"""

# import modules and declare variables
import os
import numpy as np
import pandas as pd
import random
from sklearn.feature_extraction.text import CountVectorizer
from wordcloud import WordCloud
import matplotlib.pyplot as plt


# flag of saving word cloud to file
F_savePNG = True

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
l_topicS = sorted(data.topicS.unique())

# get the hierarchical topic name of every abstract
data['1'] = data.topic.str.extract('^\+\+(\w).*')
data['2'] = data.topic.str.extract('^\+\+(\w\.\d\d).*')
data['3'] = data.topic.str.extract('^\+\+(\w\.\d\d\.\w+).*')

# get the hierarchical topic list
topic_lvl = ['1','2','3']
l_topic = {}  # a dictionary
for lvl in topic_lvl:
    l_topic[lvl] = sorted(data[lvl].unique())


# ############### create word cloud  ###############

# function to generate a random color, used by word cloud generate_WC
def my_color_func(word, font_size, position, orientation, random_state=None, **kwargs):
    color_list = (\
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', \
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf', \
        # '#1f77b4','#aec7e8','#ff7f0e','#ffbb78','#2ca02c',\
        # '#98df8a','#d62728','#ff9896','#9467bd','#c5b0d5',\
        # '#8c564b','#c49c94','#e377c2','#f7b6d2','#7f7f7f',\
        # '#c7c7c7','#bcbd22','#dbdb8d','#17becf','#9edae5' \
                  )
    return color_list[random.randint(0,len(color_list)-1) ]

# funciton to generate word cloud object
fontpath = os.path.join ( current_filepath, './font/impact.ttf' )
def generate_WC(text):
    try:
        cloud = WordCloud(font_path=fontpath, width=960, height=480, ranks_only=True,  max_font_size=128, min_font_size=24, \
                      background_color='white', color_func=my_color_func)\
        .generate(text)
    except:
        cloud = WordCloud(font_path=None, width=960, height=480, ranks_only=True,  max_font_size=128, min_font_size=24, \
                      background_color='white', color_func=my_color_func)\
        .generate(text)
    return cloud

text_all = '\n'.join(data.abstract)  # join all abstract together
cloud = generate_WC(text_all)

if F_savePNG:
    path_WC_PNG = os.path.join ( current_filepath, 'WC_PNG')
    if not os.path.exists( path_WC_PNG ):
        os.makedirs( path_WC_PNG )
    name_file = os.path.join ( path_WC_PNG, 'root'+'.png' )
    cloud.to_file(name_file)


for lvl in ['1']:
    # for every topic:
    for topic in l_topic[lvl]:
        if topic is not np.nan:
            print('working on %s' % topic)
            text_cur = '\n'.join(data.abstract[data[lvl]==topic])
            cloud = generate_WC(text_cur)
            if F_savePNG:
                name_file = os.path.join ( path_WC_PNG, topic+'.png' )
                cloud.to_file(name_file)

plt.figure()
plt.imshow(cloud)
plt.axis("off")


print ('finish')
