import os
import pandas as pd
import re
from operator import itemgetter
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
import argparse

#from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.datasets import fetch_20newsgroups

n_features = 10000
n_topics = 100
n_top_words = 20
colors = ['#ff0000', '#3399ff', '#ffff00','#99ff33', '#ff3399', '#00ffcc', '#ff9933', '#cc33ff', '#009933', '#3333cc']
    
def main():
    #parser = argparse.ArgumentParser()
    #parser.add_argument('-dim', default='pca', help='Method for dimension reduction')
    #parser.add_argument('-c', default='kmeans', help='Method for clustering')
    #parser.add_argument('-recommend', default='false', help='Paper ID to which related papers will be listed')
    #parser.add_argument('-nfeature', default=3000, help='number of features (key words)')
    #opts = parser.parse_args()
    data = load_file('abstract_data.csv')
    (text_tf,vectorizer) = get_text_feature(data['abstract'])
    fit_lda(text_tf,vectorizer)
    
# ========== load data csv ==========
def load_file(file_name):    
    current_filepath = os.path.dirname(__file__)
    data_filepath = os.path.join(current_filepath, '../DATA/'+file_name)
    if file_name=='abstract_data.csv':
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
    elif file_name=='stopwords.txt':
        with open(data_filepath) as datafile:
            data = []
            for word in datafile.readlines():
                data.append(word)
    return(data)

# ========== get text feature ==========
def get_text_feature(corpus):
    # input is a list of strings
    vectorizer = CountVectorizer(strip_accents='unicode',stop_words='english',min_df=1,max_df=0.95,max_features=n_features,tokenizer=tokenize)
    text_tf = vectorizer.fit_transform(corpus)
    return [text_tf, vectorizer]
    
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
    lda = LatentDirichletAllocation(n_topics=n_topics, max_iter=5,learning_method='online', learning_offset=50.,random_state=0)
    lda.fit(tf)
    tf_feature_names = vectorizer.get_feature_names()
    print_top_words(lda, tf_feature_names, n_top_words)

def print_top_words(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print("Topic #%d:" % topic_idx)
        print(" ".join([feature_names[i]
                        for i in topic.argsort()[:-n_top_words - 1:-1]]))
    return

    
def d_reduction(X):    
    if opts.dim is 'pca':
        from sklearn.decomposition import PCA
        X = PCA(n_components=3).fit_transform(X)
    elif opts.dim is 'tsne':
        from sklearn.manifold import TSNE
        X = TSNE(n_components=10, random_state=0).fit_transform(X) 
    return X
    
def cluster(X):
    if opts.c=='kmeans':
        n_clusters = 7
        labels = kmeans(X,n_clusters)
    elif opts.c=='dbscan':
        labels = dbscan(X)
    
    if opts.recommend != 'false':
        if opts.recommend in Title:
            Title = np.array(Title)
            X_ID = X[list(Title).index(opts.recommend)]
            distances = np.sqrt(np.sum((X-X_ID)**2,1))
            min_distances = distances.argsort()[:6]
            min_distances_Title = Title[min_distances]
            print '5 papers related to ' + str(min_distances_Title[0]) + '. ' + Title[min_distances[0]]
            for i in range(1,len(min_distances_Title)):
                print str(min_distances_Title[i]) + '. ' + Title[min_distances[i]]
        else:
            print 'Wrong paper Title'
        
    
    plt.show()
    
            
            
def kmeans(X,n_clusters):
    from sklearn.cluster import KMeans
    fig = plt.figure(figsize=(5, 5))
    k_means = KMeans(init='k-means++', n_clusters=n_clusters, n_init=20)
    k_means.fit(X)
    labels = k_means.labels_
    plot_clusters(fig,colors[:n_clusters],X,labels,'K-means pc1-pc')   
      
    return(labels)
    
    
def dbscan(X):
    from sklearn.cluster import DBSCAN
    fig = plt.figure(figsize=(5, 5))
    db = DBSCAN(eps=0.6, min_samples=10).fit(X)
    core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
    core_samples_mask[db.core_sample_indices_] = True
    labels = db.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    labels_new = labels
    labels_new[labels==-1] = n_clusters
    colorsss = colors[:n_clusters]
    colorsss.append('#ffffff')
    plot_clusters(fig,colorsss,X,labels_new,'DBSCAN pc1-pc')   
    
    return labels

def plot_clusters(fig,colors,X,labels,plttitle):
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.set_axis_bgcolor('black')
    for k, col in zip(range(len(colors)), colors):
        my_members = labels == k
        ax1.plot(X[my_members, 0], X[my_members, 1], 'w.',
                markerfacecolor=col, marker='.')
    ax1.set_title(plttitle+'2')
    ax1.set_xticks(())
    ax1.set_yticks(())
    
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.set_axis_bgcolor('black')
    for k, col in zip(range(len(colors)), colors):
        my_members = labels == k
        ax2.plot(X[my_members, 0], X[my_members, 2], 'w.',
                markerfacecolor=col, marker='.')
    ax2.set_title(plttitle+'3')
    ax2.set_xticks(())
    ax2.set_yticks(())

    

if __name__ == '__main__':
  	main()
