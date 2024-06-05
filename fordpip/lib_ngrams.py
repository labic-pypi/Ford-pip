#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import nltk

from collections import defaultdict
from csv import reader, writer, QUOTE_MINIMAL

import pandas as pd

from .lib_input import filename_append, get_file_delimiter, time_to_print
from .lib_stopwords import STOPWORDS
from .lib_text import process_word

def ngrams_parse(input_name, n_value=None, keywords=[], min_len=2):

    output = []

    if isinstance(keywords, str):
        keywords = keywords.replace(', ', ',').split(',') if keywords else []

    with open(input_name, 'rt', encoding='utf8') as input_file:
        for line in input_file.readlines():
            words = [process_word(x) for x in line.lower().split()]
            grams = nltk.ngrams([w for w in words if w], n_value)

            for g in grams:
                cond1 = all(w != '' for w in g)
                cond2 = any(w not in STOPWORDS for w in g)
                cond3 = all(not w.startswith('http') for w in g)
                cond4 = (keywords == [] or any(w in g for w in keywords))

                if cond1 and cond2 and cond3 and cond4:
                    gram = list(g)
                    output.append(gram)

    if not output:
        print(f'No n-grams found with keywords: {keywords}.')
        return output

    list_output = []
    dict_output = defaultdict(int)

    for v in output:
        tup = tuple(v)
        dict_output[tup] += 1

    for i,v in enumerate(output):
        tup = tuple(v)
        output[i].append(dict_output[tup])

    columns = str('n-'*(n_value)).split('-')
    columns = [(v+'-'+str(i+1)) for i,v in enumerate(columns[:-1])] # +[columns[-1]]

    df = pd.DataFrame(output)
    df.columns = columns+['count']
    df.drop_duplicates(inplace=True)
    df.sort_values('count', inplace=True, ascending=False)
    
    print(f"Writing {df.shape[0]} n-grams to 'ngrams.csv'...")
    df.to_csv('ngrams.csv', index=False)