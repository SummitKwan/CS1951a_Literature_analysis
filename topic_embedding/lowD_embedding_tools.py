import os
import pandas as pd
import json
import numpy as np
from scipy.sparse import csr_matrix, csc_matrix, lil_matrix, hstack, vstack
import copy
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.manifold import TSNE
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.decomposition import PCA, IncrementalPCA, KernelPCA, FastICA
import sklearn.preprocessing
from scipy.spatial.distance import pdist, cdist, squareform
from scipy.stats.mstats import zscore
import matplotlib
import matplotlib.pyplot as plt


# ========== load data csv ==========
def load_file(file_name):
    current_filepath = os.path.dirname(__file__)
    data_filepath = os.path.join(current_filepath, '../DATA/'+file_name)
    if file_name=='abstract_data.csv':
        with open(data_filepath) as datafile:
            data = pd.read_csv(datafile)
        # ========== remove duplicates ==========
        data.drop_duplicates(inplace=True)
        # ========== fields to keep ==========
        data = data[['topic', 'abstract','pres_title']]
        # get the 1,2,3 hierachy of the topics
        data['1'] = data.topic.str.extract('^\+\+(\w).*')
        data['2'] = data.topic.str.extract('^\+\+(\w\.\d\d).*')
        data['3'] = data.topic.str.extract('^\+\+(\w\.\d\d\.\w+).*')
        data.sort('3')
        # remove rows with nan topic
        data = data[data['1'].apply(lambda x: x is not np.nan)]
    elif file_name=='stopwords.txt':
        with open(data_filepath) as datafile:
            data = []
            for word in datafile.readlines():
                data.append(word)
    elif file_name == 'topic_list.csv':
        with open(data_filepath) as topicfile:
            data = pd.read_csv(topicfile)
    return(data)

# ---------- read topic info, and add full name to data ----------
def replace_topic_fullname(data):
    topic = load_file('topic_list.csv')

    data_fullname = copy.deepcopy(data)

    data1 = pd.merge(data,topic[['i','text']],how='left',left_on='1',right_on='i')
    data_fullname['1']=data1['text'].tolist()

    data2 = pd.merge(data,topic[['i','text']],how='left',left_on='2',right_on='i')
    data_fullname['2']=data2['text'].tolist()

    data3 = pd.merge(data,topic[['i','text']],how='left',left_on='3',right_on='i')
    data_fullname['3']=data3['text'].tolist()

    data_fullname = data_fullname[data_fullname['1'].apply(lambda x: x is not np.nan)]
    return [data_fullname, topic]


# ---------- get text feature ----------
def get_text_feature(corpus):
    # input is a list of strings

    vectorizer = CountVectorizer(strip_accents='unicode',stop_words='english',min_df=5, tokenizer=tokenize)
    text_tf = vectorizer.fit_transform(corpus)
    # suppress large counts
    text_tf = text_tf.power(0.5)
    # make the sum of all feature of every abstract to be 1.0
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
    # xc = csr_matrix(xc)
    return [xc, yc]

# ---------- tSNE embedding ----------
def embed(x):
    model = TSNE(n_components=2, random_state=0, perplexity=50.0, metric='correlation')
    # model = TSNE(n_components=2, random_state=0, perplexity=50.0)
    # model = KernelPCA(n_components=2, kernel='rbf')
    # model = PCA(n_components=2)
    # model = FastICA(n_components=2)
    return model.fit_transform(x)

# ---------- low-D embed for the hierarchical data ----------
def embed_hierarchy(x, yy):
    # mean feature by level of abstract
    [x1,y1] = group_mean_x(x, yy['1'])
    [x2,y2] = group_mean_x(x, yy['2'])
    [x3,y3] = group_mean_x(x, yy['3'])
    # x4 = x.todense()
    # y4 = np.array(yy['1'])

    # concatenate x,y for embedding, h is the level (1,2,or 3)
    xh = np.concatenate((x1,x2,x3))
    yh = np.concatenate((y1,y2,y3))
    h  = np.concatenate((np.ones(len(y1))*1, np.ones(len(y2))*2, np.ones(len(y3))*3))

    # low-D embedding
    print('start embedding')
    xh_ld = embed(xh)

    # zscore for plotting
    xh_ld_z = zscore(xh_ld, axis=0)

    # coloring scheme
    mycolor = gen_distinct_color(len(y1))
    y_to_c = dict(zip([y[0] for y in y1], mycolor))   # y to color dictionary, based on top level
    ch = [y_to_c[i] for i in [y[0] for y in yh]]  # get color for every data point

    embed_results = {'xh_ld':xh_ld, 'xh_ld_z':xh_ld_z, 'xh':xh, 'yh':yh, 'h':h, 'ch':ch,'y1':y1}

    return embed_results

def plot_embed_result(embed_results):
    xh_ld_z = embed_results['xh_ld_z']
    h  = embed_results['h']
    ch = embed_results['ch']
    y1 = embed_results['y1']

    fig = plt.figure()
    fig.patch.set_facecolor('white')
    for i in range(len(y1)):
        plt.scatter(xh_ld_z[i,0],xh_ld_z[i,1],s=300/h**3, c=ch[i], edgecolors='none' )
    # plt.legend( list(y1), loc='upper center', bbox_to_anchor=(1, 1) )
    plt.scatter(xh_ld_z[:,0],xh_ld_z[:,1],s=300/h**3, c=ch, edgecolors='none' )
    plt.axis('off')


def save_embed_results_for_D3(embed_results):

    embed_results['x'] = embed_results['xh_ld_z'][:,0]
    embed_results['y'] = embed_results['xh_ld_z'][:,1]

    key_list = ['x','y','h','yh','ch']  # specify the list to keys to save
    df_save = {key:embed_results[key] for key in key_list}

    # save to json
    current_filepath = os.path.dirname(__file__)
    data_filepath = os.path.join(current_filepath, './topic_embedding.json')
    pd.DataFrame.from_dict( df_save ).to_json(data_filepath , orient='records')


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
        distinct_color.append( matplotlib.colors.rgb2hex( matplotlib.colors.hsv_to_rgb([hi,0.6,0.90]) )  )
    return distinct_color


# ---------- for count vectorizer ----------
def tokenize(text):
    text = re.sub('[\.\,\/\\\&\=\:\;\"\(\)\[\]\{\}\?\!\$\*]','',text)
    stopwords = load_file('stopwords.txt')
    tokens = []
    for word in text.split():
        if word[0].isupper() and word[-1].islower():
            word = word.lower()
        if word not in stopwords:
            tokens.append(word)
    return tokens


def fit_lda(tf,vectorizer):
    n_topics = 20
    n_top_words = 20
    lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,learning_method='online', learning_offset=50.,random_state=0)
    tf_lda = lda.fit_transform(tf)

    f_print = True
    if f_print:
        tf_feature_names = vectorizer.get_feature_names()
        print_top_words(lda, tf_feature_names, n_top_words)

    return [tf_lda,lda]


def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    return 0

def get_neighbor(x_lda, q, n):
    # x: all abstract N*M
    # q: query abstract 1*M, or index
    # n: number of neighbors to return
    if type(q) is int:
        dist = cdist (x_lda, x_lda[[q],:], 'euclidean')
    else:
        dist = cdist (x_lda, q, 'euclidean')
    return np.argsort(dist, axis=None)[0:n]
