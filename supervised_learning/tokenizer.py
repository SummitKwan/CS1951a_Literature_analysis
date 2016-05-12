import string
import re

class Tokenizer(object):
    def __init__(self):
        pass


    def process(self, my_str):

        my_str = my_str.lower()

        my_str = ''.join([c for c in my_str if not c in set(string.punctuation)])

        return my_str

    def __call__(self, my_str):

        features = []
        for word in self.process(my_str).split():
            features.append(word)

        return features