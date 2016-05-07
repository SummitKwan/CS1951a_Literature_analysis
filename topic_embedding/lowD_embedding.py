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

    print('lowD embedding')
    x = text_tf
    yy= data[['1','2','3']]

    print('recommendation based on similarity')
    x_d = np.asarray(x.todense())

    embed_results = embed_hierarchy(text_tf, data_full[['1','2','3']])
    plot_embed_result(embed_results)
    print('saving embedding results to json')
    save_embed_results_for_D3(embed_results)

    # [x_lda_out,lda] = fit_lda(x,vectorizer)

    print('stop')

    return 'finish'


if __name__ == '__main__':
  	main()