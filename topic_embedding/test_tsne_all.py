"""

aim: low dimensional embedding based on ngrams of the sfn abstracts

Shaobo Guan, Ruobing Xia, 2016-0423, SAT
"""

# import modules
import os
from lowD_embedding_tools import *
import lowD_embedding_tools; reload(lowD_embedding_tools); from lowD_embedding_tools import *
import time

# ========== get current file path and path to datafile ==========
current_filepath = os.path.dirname(__file__)
data_filepath = os.path.join(current_filepath, '../DATA/abstract_data.csv')
topic_filepath= os.path.join(current_filepath, '../DATA/topic_list.csv')




print('loading data')
data = load_file('abstract_data.csv')
[data_full,topics] = replace_topic_fullname(data)

print('calculating text features')
# (data_fullname, topic) = replace_topic_fullname(data)
[text_tf, vectorizer] = get_text_feature(data['abstract'])

print('lowD embedding')
x = text_tf
model = TSNE(n_components=2, random_state=0, perplexity=50.0, metric='correlation')

t0=time.time()
x_l = model.fit_transform(x[:100,:])
print(time.time()-t0)