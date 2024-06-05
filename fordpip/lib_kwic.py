#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import argparse
import pandas as pd
import string
import sys

from collections import defaultdict
from .lib_stopwords import STOPWORDS
from .lib_text import process_word

SIZE = 5

def kwic_parse(input_name, keywords, size=SIZE, max_keywords=3, ignore_case=True):

    size += 1
    output = []

    if isinstance(keywords, str):
        keywords = keywords.replace(', ', ',').split(',') if keywords else []

    if not keywords:
        keywords = set()
        dict_int = defaultdict(int)
        # count each word occurrence
        with open(input_name, 'rt', encoding='utf8') as input_file:
            for line in input_file.readlines():
                for w in line.split():
                    word = process_word(w.lower() if ignore_case else w)
                    dict_int[word] += 1
        # append items to list
        top_words = []
        for word, value in dict_int.items():
            if word and word.lower() not in STOPWORDS:
                top_words.append([word, value])
        # sort by most occurrences
        top_words.sort(key=lambda x:x[1], reverse=True)
        keywords = [w[0] for w in top_words][:max_keywords]
        print('Keywords set as: %s.\n' % keywords)

    if ignore_case:
        keywords = [keyword.lower() for keyword in keywords]

    with open(input_name, 'rt', encoding='utf8') as input_file:
        for line in input_file.readlines():
            for keyword in keywords:
                token_chain = []
                original_chain = line.strip().split()

                if ignore_case:
                    line = line.lower()

                token_chain.extend(line.strip().split())

                for i, token in enumerate(token_chain):
                    if keyword in token:
                        for punct in string.punctuation:
                            token_chain[i] = token_chain[i].strip(punct)

                while token_chain.count(keyword) > 0:
                    idx = token_chain.index(keyword)
                    end = len(token_chain)

                    start_ctxt = str()
                    end_ctxt = str()

                    if idx-1 < 0:
                        pass
                    elif idx-size < 0:
                        start_ctxt = ' '.join(original_chain[:idx-1])
                    else:
                        start_ctxt = ' '.join(original_chain[idx-size+1:idx])

                    if idx+1 >= end:
                        pass
                    elif idx+size >= end:
                        end_ctxt = ' '.join(original_chain[idx+1:])
                    else:
                        end_ctxt = ' '.join(original_chain[idx+1:idx+size])

                    if len(original_chain[idx]) > len(token_chain[idx]):
                        head, tail = original_chain[idx].lower().split(token_chain[idx].lower(),1)
                        original_chain[idx] = original_chain[idx].lstrip(head).rstrip(tail)
                        start_ctxt = str(start_ctxt + ' ' + head).lstrip()
                        end_ctxt = str(tail + ' ' + end_ctxt).rstrip()

                    output.append([start_ctxt, original_chain[idx], end_ctxt])
                    original_chain = original_chain[idx+1:]
                    token_chain = token_chain[idx+1:]

    for left_ctxt, keyword, right_ctxt in output[:10]:
        print("{0:{3}}\t{1:{4}}\t{2:{3}}".format(left_ctxt, keyword, right_ctxt, 5*size, len(keyword)))

    if len(output)>10:
        print(f'... ({len(output)-10}) more objects)')

    list_output = []
    dict_output = defaultdict(int)

    for v in output:
        tup = tuple(v)
        dict_output[tup] += 1

    for i,v in enumerate(output):
        tup = tuple(v)
        output[i].append(dict_output[tup])

    columns = ['left_ctxt', 'keyword', 'right_ctxt', 'count']
    
    df = pd.DataFrame(output)
    df.columns = columns
    df.drop_duplicates(inplace=True)
    df.sort_values('count', inplace=True, ascending=False)
    
    print(f"\nWriting {df.shape[0]} lines to 'kwic.csv'...")
    df.to_csv('kwic.csv', index=False)