"""

aim: get the list of SfN topics,
data source: topic_list.txt

Shaobo Guan, 2016-0321, MON
"""

# import modules
import os
import pandas as pd
import numpy as np
import json

# ========== get current file path and path to datafile ==========
current_filepath = os.path.dirname(__file__)
data_filepath = os.path.join(current_filepath, '../DATA/topic_list.txt')

# ========== read file into text ==========
with open(data_filepath) as datafile:
    text = datafile.read()


def replace_nextline():
    text = text.replace('^(\w[^\s]*)\..*')  # replace the '\r' with '\n', and save to file
    with open(data_filepath,'w') as datafile:
        datafile.write( text )

# ========== create pandas dataframe ==========
df = pd.DataFrame({'text':text.splitlines()})
df['i'] = df.text.str.extract('^(\w[^\s]*)\..*')
df['1'] = df.text.str.extract('^(\w)\..*')
df['2'] = df.text.str.extract('^(\w\.\d\d).\.*')
df['3'] = df.text.str.extract('^(\w\.\d\d\.\w+).\ .*')

def print_full_df():
    with pd.option_context('display.max_rows', 999, 'display.max_columns', 10):
        print df

def save_topic_list():
    df.to_csv(os.path.join(current_filepath, '../DATA/topic_list.csv'))

# print_full_df()
save_topic_list()