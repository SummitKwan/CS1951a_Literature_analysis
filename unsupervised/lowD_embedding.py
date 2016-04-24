"""

aim: low dimensional embedding based on ngrams of the sfn abstracts

Shaobo Guan, Ruobing Xia, 2016-0423, SAT
"""

# import modules
import os
import pandas as pd
import json
import numpy as np
import copy
from sklearn.feature_extraction.text import CountVectorizer

# ========== get current file path and path to datafile ==========
current_filepath = os.path.dirname(__file__)
data_filepath = os.path.join(current_filepath, '../DATA/abstract_data.csv')
topic_filepath= os.path.join(current_filepath, '../DATA/topic_list.csv')


def main():
    with open(data_filepath) as datafile:
        data = pd.read_csv(datafile)

    # ========== only keep topic field ==========
    data = data[['topic', 'abstract','pres_title']]
    # get the 1,2,3 hierachy of the topics
    data['1'] = data.topic.str.extract('^\+\+(\w).*')
    data['2'] = data.topic.str.extract('^\+\+(\w\.\d\d).*')
    data['3'] = data.topic.str.extract('^\+\+(\w\.\d\d\.\w+).*')
    data.sort('3')

    # remove rows with nan topic
    data = data[data['1'].apply(lambda x: x is not np.nan)]

    # (data_fullname, topic) = replace_topic_fullname(data)
    [text_tf, vectorizer] = get_text_feature(data['abstract'][0:100])

    return 'finish'


# ========== read topic info, and add full name to data ==========
def replace_topic_fullname(data):
    with open(topic_filepath) as topicfile:
        topic = pd.read_csv(topicfile)
    data_fullname = copy.deepcopy(data)

    data1 = pd.merge(data,topic[['i','text']],how='left',left_on='1',right_on='i')
    data_fullname['1']=data1['text']

    data2 = pd.merge(data,topic[['i','text']],how='left',left_on='2',right_on='i')
    data_fullname['2']=data2['text']

    data3 = pd.merge(data,topic[['i','text']],how='left',left_on='3',right_on='i')
    data_fullname['3']=data3['text']

    return (data_fullname, topic)

# ========== get text feature ==========
def get_text_feature(corpus):
    # input is a list of strings
    vectorizer = CountVectorizer(strip_accents='unicode',stop_words='english',min_df=1)
    text_tf = vectorizer.fit_transform(corpus)
    return [text_tf, vectorizer]


if __name__ == '__main__':
  	main()