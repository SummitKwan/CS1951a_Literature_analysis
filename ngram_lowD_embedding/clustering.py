import csv
import string
import re
from operator import itemgetter
from collections import Counter
import numpy as np
import matplotlib.pyplot as plt
from copy import copy 
import argparse

colors = ['#ff0000', '#3399ff', '#ffff00','#99ff33', '#ff3399', '#00ffcc', '#ff9933', '#cc33ff', '#009933', '#3333cc']
    
def load_file_NIPS(file_path):
    with open(file_path, 'r') as file_reader:
        reader = csv.reader(file_reader)
        next(reader, None)
        ID=[];Title=[];EventType=[];PdfName=[];Abstract=[];Paper=[];
        for row in reader:
            ID.append(row[0])
            Title.append(row[1])
            EventType.append(row[2])
            PdfName.append(row[3])
            Abstract.append(row[4])
            Paper.append(row[5])
    return(ID, Title, EventType, PdfName, Abstract, Paper)

def get_word_list(array):
    with open('./tools/stopwords.txt') as stopwords:
        stops = list(stopwords.read().splitlines())
    new_array = [[]]*len(array)
    for i in range(0,len(array)):
        new_array_i = re.sub('[\.\,\/\\\&\=\:\;\"\(\)\[\]\{\}\?\!\$\+\*]','',array[i]) 
        new_array_i = new_array_i.split()
        for j in range(0,len(new_array_i)):
            word = new_array_i[j].lower()
            if word not in stops:
                #word = porter_stemmer.PorterStemmer().stem(word, 0, len(word) - 1)
                if len(list(word))>2:
                    if list(word)[-2:]==['e','s'] or list(word)[-2:]==['e','d']:
                        word = ''.join(list(word)[:-2])
                if list(word)[-1]=='s' or list(word)[-1]=='e':
                    word = ''.join(list(word)[:-1])
                new_array_i[j] = word 
            else:
                new_array_i[j] = None 
        new_array[i] = [x for x in new_array_i if x != None]
        
        for j in range(0,len(new_array[i])-1):
            new_array[i].append(new_array[i][j]+' '+new_array[i][j+1])
    return(new_array)
    
def get_word_freqs(word_list,min_freq,num_kw):
    words = [item for sublist in word_list for item in sublist]
    freqs = Counter(words)    
    sorted_freqs = sorted([[x,freqs[x]/len(words)] for x in freqs if freqs[x]>min_freq],key=itemgetter(1),reverse=True)
    if num_kw>len(sorted_freqs):
        num_kw = len(sorted_freqs) 
    return(sorted_freqs[:num_kw])
    
def get_bag_of_words(word_list,key_words):
    hists = [[]]
    for i in range(len(word_list)):
        counts = Counter(word_list[i])
        hist = [0]*len(key_words)
        for word in counts:
            if word in key_words:
                hist[key_words.index(word)] = counts[word]
        if i==0:
            hists[0] = hist
        else:
            hists.append(hist)
    return(hists)
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dim', default='pca', help='Method for dimension reduction')
    parser.add_argument('-c', default='kmeans', help='Method for clustering')
    parser.add_argument('-recommend', default='false', help='Paper ID to which related papers will be listed')
    parser.add_argument('-nfeature', default=3000, help='number of features (key words)')
    opts = parser.parse_args()
    [ID, Title, EventType, PdfName, Abstract, Paper] = load_file_NIPS('./NIPS_databases/Papers.csv')
    words = get_word_list(Abstract)
    KW = get_word_freqs(words,1,opts.nfeature)
    hists = get_bag_of_words(words,[x[0] for x in KW])
    X = np.array(hists)
    if opts.dim is 'pca':
        from sklearn.decomposition import PCA
        X = PCA(n_components=3).fit_transform(X)
    elif opts.dim is 'tsne':
        from sklearn.manifold import TSNE
        X = TSNE(n_components=10, random_state=0).fit_transform(X) 
    
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
    
#    with open('results/labels.csv', 'w') as file_writer:
#        writer = csv.writer(file_writer)
#        writer.writerow(['ID', 'Title', 'PdfName', 'Abstract', 'Label_'+opts.dim+'_'+opts.c] )
#        for i in range(0,len(ID)):
#            writer.writerow([ID[i], Title[i], PdfName[i], Abstract[i], labels[i]] )   
            
            
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
