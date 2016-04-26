"""

aim: low dimensional embedding based on ngrams of the sfn abstracts

Shaobo Guan, Ruobing Xia, 2016-0423, SAT
"""

# import modules
import os
import pandas as pd
import json
import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, lil_matrix
import copy
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA, IncrementalPCA
import sklearn.preprocessing
import matplotlib
import matplotlib.pyplot as plt

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
    [text_tf, vectorizer] = get_text_feature(data['abstract'])


    embed_hierarchy(text_tf, data[['1','2','3']])


    return 'finish'


# ---------- read topic info, and add full name to data ----------
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


# ---------- get text feature ----------
def get_text_feature(corpus):
    # input is a list of strings

    vectorizer = CountVectorizer(strip_accents='unicode',stop_words='english',min_df=5)
    text_tf = vectorizer.fit_transform(corpus)
    text_tf = sklearn.preprocessing.normalize(text_tf.astype('float'),norm='l1', axis=1)
    return [text_tf, vectorizer]

# ---------- group x according to y ----------
def group_mean_x(x, y):
    y = np.array(y)
    yc = np.sort(np.unique(y)) # unique categories
    C = len(yc)    # number of categories
    [N,M] = x.shape
    # xc = csc_matrix( np.zeros([C,M]) )
    xc = np.zeros((C,M))

    for i in range(C):
        yi = yc[i]

        # xc[i,:] = sparse_matrix_mean( x[y==yi, :] )
        xc[i,:] = x[y==yi, :].mean(axis=0)  # explode memory because it converts sparse matrix to dense to do mean()
    return [xc, yc]

# ---------- tSNE embedding ----------
def embed(x):
    model = TSNE(n_components=2, random_state=0, perplexity=30.0, metric='correlation')
    # model = IncrementalPCA(n_components=2)
    return model.fit_transform(x)

# ---------- low-D embed for the hierarchical data ----------
def embed_hierarchy(x, yy):
    [x1,y1] = group_mean_x(x, yy['1'])
    [x2,y2] = group_mean_x(x, yy['2'])
    [x3,y3] = group_mean_x(x, yy['3'])

    # xh = x1
    # yh = y1
    # h  = np.ones(len(y1))

    # xh = x3
    # yh = y3
    # h  = np.ones(len(y3))*3

    # xh = np.concatenate((x1,x2))
    # yh = np.concatenate((y1,y2))
    # h  = np.concatenate((np.ones(len(y1))*1, np.ones(len(y2))*2))

    xh = np.concatenate((x1,x2,x3))
    yh = np.concatenate((y1,y2,y3))
    h  = np.concatenate((np.ones(len(y1))*1, np.ones(len(y2))*2, np.ones(len(y3))*3))

    # low-D embedding
    print('start embedding')
    xh_ld = embed(xh)

    # color
    mycolor = gen_distinct_color(len(y1))

    y_to_c = dict(zip(y1, mycolor))
    ch = [y_to_c[i] for i in [y[0] for y in yh]]


    for i in range(len(y1)):
        plt.scatter(xh_ld[i,0],xh_ld[i,1],s=300/h**3, c=ch[i], edgecolors='none' )
    plt.legend( list(y1), loc='upper left', bbox_to_anchor=(1, 1) )
    plt.scatter(xh_ld[:,0],xh_ld[:,1],s=300/h**3, c=ch, edgecolors='none' )


    # return [xh, yh, h]

# ---------- color for pretty plot ----------
def gen_distinct_color(n):
    # use golden ratio
    golden_ratio_conjugate = 0.618033988749895

    # use golden ratio
    # h = np.arange(n, dtype='float') *golden_ratio_conjugate %1

    # use spectrum
    h = np.arange(n, dtype='float') / n + 0.5/n
    distinct_color = []
    for hi in h:
        distinct_color.append( matplotlib.colors.hsv_to_rgb([hi,0.5,0.95]) )
    return distinct_color

if __name__ == '__main__':
  	main()