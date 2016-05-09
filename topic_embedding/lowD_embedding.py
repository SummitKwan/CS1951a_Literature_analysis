"""

aim: low dimensional embedding based on ngrams of the sfn abstracts

Shaobo Guan, Ruobing Xia, 2016-0423, SAT
"""

# import modules
import os
from lowD_embedding_tools import *
import lowD_embedding_tools; reload(lowD_embedding_tools); from lowD_embedding_tools import *

# ========== get current file path and path to datafile ==========
current_filepath = os.path.dirname(__file__)
data_filepath = os.path.join(current_filepath, '../DATA/abstract_data.csv')
topic_filepath= os.path.join(current_filepath, '../DATA/topic_list.csv')


def main():

    print('loading data')
    data = load_file('abstract_data.csv')
    [data_full,topics] = replace_topic_fullname(data)

    print('calculating text features')
    # (data_fullname, topic) = replace_topic_fullname(data)
    [text_tf, vectorizer] = get_text_feature(data['abstract'])
    x = text_tf
    x_d = np.asarray(x.todense())

    print('recommendation based on similarity')
    data_simple = data[['pres_title','1','2','3']]
    q=0
    recmd = get_neighbor(x_d, q, 10)
    print(data_simple.iloc[recmd])
    print(np.array(data_simple.iloc[recmd]['pres_title']))

    # low-D embedding of categories
    print('lowD embedding of topics')
    yy= data[['1','2','3']]
    embed_results = embed_hierarchy(text_tf, data_full[['1','2','3']])
    plot_embed_result(embed_results)
    print('saving embedding results to json')
    save_embed_results_for_D3(embed_results)

    # low-D embedding of all abstracts: super slow, can take more than one hour!
    if False:
        print('lowD embedding of all abstracts')
        t0=time.time()
        x_all_l = embed(x_d[:,:])
        if False:
            np.savetxt('x_l_tsne.csv', delimiter=',', newline='\n')
        print('time takes: '+ str((time.time()-t0)) +' s')
        plot_embed_all_abstract(x_l, topic)  # plot

    # plot embedding of all abstracts:
    x_l = np.loadtxt('x_l_tsne.csv', delimiter=',')
    plt.scatter(x_l[:,0],x_l[:,1])

    # recoomendation with t-sne
    data_simple = data[['pres_title','1','2','3']]
    q=0
    recmd = get_neighbor(x_l, q, 10)
    print(data_simple.iloc[recmd])
    print(np.array(data_simple.iloc[recmd]['pres_title']))

    # compare native vs t-sne recommendation system: t-sne with euclidiean distance seems better
    q=12540
    print(data_simple.iloc[get_neighbor(x_l, q, n=10, method_dist='euclidean')])
    print(data_simple.iloc[get_neighbor(x_d, q, n=10, method_dist='cosine')])
    print(np.array(data_simple.iloc[get_neighbor(x_l, q, n=10, method_dist='euclidean')]['pres_title']))
    print(np.array(data_simple.iloc[get_neighbor(x_d, q, n=10, method_dist='cosine')]['pres_title']))

    return 'finish'


if __name__ == '__main__':
  	main()