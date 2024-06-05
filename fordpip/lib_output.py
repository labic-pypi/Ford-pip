#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions used to output the results of the script.

The constants used in it are:

    * MAX_WORDS_NUMBER_CSV: maximum number of words to be present in
    the top_words.csv file;

    * MAX_WORDS_NUMBER_WORDCLOUD: maximum number of words to be in the TXT
    file that will be used to generate the wordcloud;
'''

from csv import writer, QUOTE_MINIMAL

from .lib_input import normalize_dict, str_pct
from .lib_text import *
from .lib_time import *

try: from requests import post
except: print('Warning: failed to import python3-requests.')

MAX_WORDS_NUMBER_CSV = 1000
MAX_WORDS_NUMBER_WORDCLOUD = 120

def expand_comments_per_post(dict_likes_count):
    '''
    Expand comments per post on Netvizz datasets.
    '''
    list_top_comments = []

    for post_id, list_of_comments in dict_likes_count.items():
        for tup_comment_like in list_of_comments:
            list_top_comments.append([post_id, tup_comment_like[0], tup_comment_like[1], tup_comment_like[2]])

    return list_top_comments

def int_dictionary_to_csv(filename, int_dict_in, column_titles, delimiter=','):
    '''
    Writes a CSV file in the following format:
    > post_type | interactions_# | %_of_total
    Interactions can be shares, likes or comments.
    '''
    total = sum(int_dict_in.values())
    float_dict_post_percent = {}

    for key, value in sorted(int_dict_in.items()):
        float_dict_post_percent[key] = (value * 100)/total

    with open(filename, 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(column_titles)

        for key, value in sorted(float_dict_post_percent.items()):
            file_writer.writerow([key, int_dict_in[key], str_pct(value)])

def int_dictionary_interactions_summary_to_csv(filename,
    int_dict_likes_in, int_dict_comments_in, int_dict_shares_in, delimiter=','):
    '''
    Writes a CSV file in the following format:
    > date (dd/mm/yyyy) | post_type | post_text| interactions_#
    Interactions can be shares, likes or comments.
    Post type can be status, photo, video or link.
    '''
    column_titles = ['post_type', 'likes', 'likes_%', 'comments', 'comments_%', 'shares', 'shares_%']
    total_likes = sum(int_dict_likes_in.values())
    total_comments = sum(int_dict_comments_in.values())
    total_shares = sum(int_dict_shares_in.values())

    with open(filename, 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(column_titles)

        for key in int_dict_comments_in.keys():
            try: pct_likes = (int_dict_likes_in[key]*100)/total_likes
            except ZeroDivisionError: pct_likes = int(0)
            try: pct_comments = (int_dict_comments_in[key]*100)/total_comments
            except ZeroDivisionError: pct_comments = int(0)
            try: pct_shares = (int_dict_shares_in[key]*100)/total_shares
            except ZeroDivisionError: pct_shares = int(0)
            file_writer.writerow([key, int_dict_comments_in[key], str_pct(pct_comments),
                                  int_dict_likes_in[key], str_pct(pct_likes),
                                  int_dict_shares_in[key], str_pct(pct_shares)])

def interactions_summary_to_csv(filename, list_summary, column_titles, delimiter=','):
    '''
    Writes a CSV file in the following format:
    > dd/mm/YYYY | post_type | post_text | interactions_#
    Interactions can be shares, likes or comments.
    '''
    list_summary = sorted(list_summary, key = lambda x: x[0])

    with open(filename, 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(column_titles)

        for item in list_summary:
            date = datetime_from_timestamp(item[0])
            date = datetime_to_str(date)
            line = [date] + item[1:]
            file_writer.writerow(line)

def replace_comments_id_with_comment_text(list_comments_likes, dict_comment_id_text):
    '''
    Replace comments' ID with comments' text on Netvizz datasets.
    '''
    output = []

    for post_id_comment_id_likes_tuple in list_comments_likes:
        post_id = post_id_comment_id_likes_tuple[0]
        comment_id = post_id_comment_id_likes_tuple[1]
        comment_likes = post_id_comment_id_likes_tuple[2]
        is_reply = post_id_comment_id_likes_tuple[3]
        comment_text = dict_comment_id_text[comment_id]
        output.append([post_id, comment_text, comment_likes, is_reply])

    return output

def replace_post_id_with_post_text(list_comments_likes, dict_post_id_text):
    '''
    Replace posts' ID with posts' text on Netvizz datasets.
    '''
    output = []

    for post_id_comment_id_likes_tuple in list_comments_likes:
        post_id = post_id_comment_id_likes_tuple[0]
        post_text = dict_post_id_text[post_id]
        comment_text = post_id_comment_id_likes_tuple[1]
        comment_likes = post_id_comment_id_likes_tuple[2]
        is_reply = post_id_comment_id_likes_tuple[3]
        output.append([post_text, comment_text, comment_likes, is_reply])

    return output

def send_request(array, url, tts=30):
    '''
    Send array to API endpoint.
    '''
    while True: # try until succeeded
        response = post(url, json=array)
        if '200' not in str(response):
            print('\nWarning: error sending data to API endpoint.')
            sleep_seconds(tts)
        else: break

def write_gdf(filename, edges, nodes=[], header_nodes=[], header_edges=[], directed=True, delimiter=','):
    '''
    Exports nodes and edges to Gephi compatible graph format.
    '''
    header_nodes = ['nodedef>name VARCHAR'] + (header_nodes if header_nodes else [])
    header_edges = ['edgedef>node1 VARCHAR', 'node2 VARCHAR'] + (header_edges if header_edges else [])
    header_edges.append('directed BOOLEAN')

    with open(filename, 'w', newline='', encoding='utf8') as graphfile:
        file_writer = writer(graphfile, delimiter=delimiter)
        file_writer.writerow(header_nodes)
        for line in nodes:
            row = list(line)
            file_writer.writerow(row)
        file_writer.writerow(header_edges)
        for line in edges:
            row = list(line)
            row.append(directed)
            file_writer.writerow(row)

def write_set(filename, set_input, header=[], delimiter=',', encoding='utf8'):
    '''
    Write a set to CSV.
    '''
    with open(filename, 'w', newline='', encoding=encoding) as f:
        file_writer = writer(f, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(header)
        for line in set_input:
            file_writer.writerow(list(line))

def write_top_comments(dict_likes_count, dict_comment_id_text, dict_post_id_text, delimiter=','):
    '''
    Write top comments on Netvizz datasets.
    '''
    all_comments = expand_comments_per_post(dict_likes_count)
    all_comments = replace_comments_id_with_comment_text(all_comments, dict_comment_id_text)
    all_comments = replace_post_id_with_post_text(all_comments, dict_post_id_text)
    all_comments_sorted = sorted(all_comments, key=lambda t:int(t[2]), reverse=True)

    with open('top_comments.csv', 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(['post_text', 'comment_text', 'likes_#', 'is_reply'])
        for item in all_comments_sorted:
            file_writer.writerow(item)

    with open('top_comments_replies.csv', 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(['post_text', 'comment_text', 'likes_#'])
        for item in all_comments_sorted:
            if item[3] == '1':
                file_writer.writerow([item[0], item[1], item[2]])

def write_values(filename, dict_in, header=[], reverse=True, pct=False, delimiter=',', encoding='utf8',
                 sort_key_function=lambda t: int(t[1]), value_format_function=lambda t: t):
                 # sort_key_function=lambda t:t, # lambda t:(t[0:2], t[3:5], t[6:8])
    '''
    Given a dictionary, a sorting function for it's keys
    a value format function to format the output, this function generates
    a CSV file with the ordered by the keys with the key as the first column
    and the value as the second. The file can be ordered in reverse.
    '''
    ordered_list = []

    for key, value in dict_in.items():
        ordered_list.append([key, value_format_function(value)])

    ordered_list = sorted(ordered_list, key=sort_key_function, reverse=reverse)
    total = sum(dict_in.values()) if pct else 0

    with open(filename, 'w', newline='', encoding=encoding) as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(header)
        for item in ordered_list[:MAX_WORDS_NUMBER_CSV]:
            pct = (item[1]*100)/total if total > 0 else 0
            file_writer.writerow([item[0], item[1], str_pct(pct)] if pct else [item[0], item[1]])

def write_timeline(filename, words_per_time, list_of_words, timestamps_list, delimiter=','):
    '''
    Write timeline to output file after filling the given period.
    '''
    grouped_by_words = {}

    if any(not i for i in [words_per_time, timestamps_list]):
        return

    for word in list_of_words:
        try: grouped_by_words[word] = word_over_time(words_per_time[word])
        except (KeyError, ValueError): pass # ValueError added on 2017-11-19

    with open(filename, 'w', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow([''] + list_of_words)

        for period in create_time_steps(timestamps_list):
            line = [datetime.strftime(period[0], '%d/%m/%y')]

            for word in list_of_words:
                try: value = grouped_by_words[word][period[1]]
                except: value = 0
                line.append(value)

            file_writer.writerow(line)

def write_to_csv(filename, line, delimiter, quoting):
    '''
    Write line to file or append if file already exists.
    '''
    with open(filename, 'a', newline='', encoding='utf8') as csvfile:
        file_writer = writer(csvfile, delimiter=delimiter, quoting=QUOTE_MINIMAL)
        file_writer.writerow(line)

def write_wordcloud(filename, dict_str_int_wordcount, sort_key_function=lambda t:t[1], value_key_function=lambda t:t):
    '''
    Writes the normalized dict in a txt to be pasted in wordle, Tagxedo
    or another wordcloud service. Entries in the dict_str_int_wordcount
    dictionary are in the format "string_word => integer_count",
    eg.: "chocolate => 10000".
    '''
    ordered_list = []

    if not dict_str_int_wordcount:
        return

    dict_str_int_wordcount = normalize_dict(dict_str_int_wordcount)

    for key, value in dict_str_int_wordcount.items():
        ordered_list.append([key, value_key_function(value)])

    ordered_list = sorted(ordered_list, key=sort_key_function, reverse=True)

    with open(filename, 'w', encoding= 'utf8') as out:
        for item in ordered_list[:MAX_WORDS_NUMBER_WORDCLOUD]:
            i = 0
            while i < int(item[1]):
                out.write(item[0] + ' ')
                i+=1