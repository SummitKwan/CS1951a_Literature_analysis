"""

aim: generate a tree structure dictionary for all the sfn topics and save it as a json file, for D3 plot

Shaobo Guan, 2016-0320, SUN
"""

# import modules
import os
import pandas as pd
import json
import numpy as np
import copy

# ========== get current file path and path to datafile ==========
current_filepath = os.path.dirname(__file__)
data_filepath = os.path.join(current_filepath, '../DATA/abstract_data.csv')
topic_filepath= os.path.join(current_filepath, '../DATA/topic_list.csv')

with open(data_filepath) as datafile:
    data = pd.read_csv(datafile)

# ========== only keep topic field ==========
data = data[['topic']]
# get the 1,2,3 hierachy of the topics
data['1'] = data.topic.str.extract('^\+\+(\w).*')
data['2'] = data.topic.str.extract('^\+\+(\w\.\d\d).*')
data['3'] = data.topic.str.extract('^\+\+(\w\.\d\d\.\w+).*')
data.sort('3')

# remove nan rows
data = data[data['1'].apply(lambda x: x is not np.nan)]

# ========== read topic info, and add full name to data ==========
def replace_topic_fullname():
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

[data_fullname, topic] = replace_topic_fullname()

def get_fullname(shortname):
    try:
        return topic[topic['i']==shortname]['text'].item()
    except:
        return ''

# ========== count number of abstracts in every level 3 topic ==========

topic_count = data.groupby('3')['1','2','3','topic'].first()
topic_count['count'] = data.groupby('3')['3'].count()

# ========== generate tree using json ==========
topic_tree = {'name':'root', 'children':[], 'fullname': 'root' }

for i in range(len(topic_count)):
    level_1 = topic_count['1'][i]
    level_2 = topic_count['2'][i]
    level_3 = topic_count['3'][i]
    level_3_full = topic_count['topic'][i]
    size    = topic_count['count'][i]

    list_1 = map((lambda x: x['name']), topic_tree['children'] )
    if level_1 not in list_1:
        topic_tree['children'].append({'name': level_1, 'children':[], 'fullname': get_fullname(level_1) })
        list_1 = map((lambda x: x['name']), topic_tree['children'] )
    i_1 = list_1.index(level_1)

    list_2 = map((lambda x: x['name']), topic_tree['children'][i_1]['children'] )
    if level_2 not in list_2:
        topic_tree['children'][i_1]['children'].append({'name': level_2, 'children':[], 'fullname': get_fullname(level_2) })
        list_2 = map((lambda x: x['name']), topic_tree['children'][i_1]['children'] )
    i_2 = list_2.index(level_2)

    list_3 = map((lambda x: x['name']), topic_tree['children'][i_1]['children'][i_2]['children'] )
    if level_3 not in list_3:
        topic_tree['children'][i_1]['children'][i_2]['children'].append({'name': level_3, 'size': size, 'fullname': get_fullname(level_3) })

# ========== save to json ==========
with open('topic_tree.json', 'w') as fp:
    json.dump(topic_tree, fp)



print('finish')