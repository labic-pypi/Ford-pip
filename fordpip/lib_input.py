#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for input data
handling and parsing, largerly used by the
"parse-facebook" and "parse-tweets" scripts.
'''

from csv import reader
from collections import defaultdict, OrderedDict
from itertools import combinations
from os.path import dirname, realpath, splitext

try: from requests import head
except: print('Warning: failed to import python3-requests.')

def add_to_dicts(key, dict_int, dict_dates={}, date=None, dict_set={}, item=None):
    '''
    Add key to dictionaries accordingly.
    '''
    dict_int[key] += 1
    dict_set[key].add(item) if item else None
    dict_dates[key].append(date) if date else None

def add_to_network(network, line):
    '''
    Add source-target relation to list.
    '''
    edge = []
    for value in line:
        value = str(value).replace(',','')\
                          .replace('\'','')\
                          .replace('"','')\
                          .replace('\n','')\
                          .replace('\r','')
        value = value[:140] + ('...' if len(str(value)) > 140 else '')
        value = value.encode(encoding='utf8', errors='ignore')\
                     .decode(encoding='utf8', errors='ignore')
        edge.append(value)
    network.append(tuple(edge))

def dict_of_int_from_dict_of_lists(dict_of_lists):
    '''
    From a given dictionary where each value is a
    list of something creates an int_dictionary where
    the keys are the same that of the argument dict but
    the values are the length of the lists in these keys.
    '''
    dict_of_ints = defaultdict(int)
    for key, list_of_strings in dict_of_lists.items():
        dict_of_ints[key] = len(list_of_strings)
    return dict_of_ints

def expand_url(str_url):
    '''
    Return full unshortened URL.
    '''
    return head(str_url, allow_redirects=True).url

def filename_append(str_filename, str_text_to_append):
    '''
    Append a string to the end of a given filename.
    '''
    str_filename, str_file_extension = splitext(str_filename)
    new_filename = str_filename + str_text_to_append + str_file_extension
    return new_filename

def get_file_delimiter(file_name, quiet=True):
    '''
    Return character delimiter from file.
    '''
    with open(file_name, 'rt', encoding='utf8') as input_file:
        file_reader = reader(input_file)
        try: header = str(next(file_reader))
        except: return '\n'

    for i in ['|', '\\t', ';', ',']:
        if i in header: # \\t != \t
            print('Delimiter set as "' + i + '".') if not quiet else None
            return i.replace('\\t', '\t')

    return '\n'

def get_file_header(file_name, lowcase=True, lst=False, title=False):
    '''
    Return field columns and positional values in a dictionary.
    '''
    fields = OrderedDict()
    delimiter = get_file_delimiter(file_name)

    with open(file_name, 'rt', encoding='utf8') as csvfile:
        csvfile = reader(csvfile, delimiter=delimiter)
        header = next(csvfile)

    if title: # done
        return header

    for column in header:
        number = header.index(column)
        title = column.encode('ascii', 'ignore').decode('ascii', 'ignore')
        xtitle = title.replace('.','_').replace(' ','_')
        title = xtitle if xtitle not in header else title
        title = title.lower() if lowcase else title
        fields[title] = number

    return fields

def get_N_first(dict_words, N=False, values=False):
    '''
    Return the N topwords of a list.
    '''
    aux = []
    top_words = []

    if N == 0: return aux

    for key, value in dict_words.items():
        top_words.append([key, value])

    top_words.sort(key=lambda x:x[1], reverse=True)

    if values: # [key,value]
        for item in top_words:
            aux.append([item[0], item[1]])
    else: # default; key only
        for item in top_words:
            aux.append(item[0])

    return aux[:N] if N else aux

def list_combinations(list_of_values):
    '''
    Return all the tuples of combinations of items in a list.
    '''
    list_of_combinations = []
    for item in combinations(list_of_values, 2):
        list_of_combinations.append([item[0], item[1]])
    return(list_of_combinations)

def list_from_list(lst, n=0):
    '''
    Return all subitems in a list.
    '''
    items=[]
    for item in lst:
        items.append(item[n])
    return items

def list_intersect(a, b):
    '''
    Return the intersection of two lists.
    '''
    return list(set(a) & set(b))

def list_unify(a, b):
    '''
    Return the union of two lists.
    '''
    return list(set(a) | set(b))

def list_unique(a):
    '''
    Return the list with duplicate elements removed.
    '''
    return list(set(a))

def load_list(filename, filter_strings=[]):
    '''
    Read a custom file if present and returns a
    list of the data in it. If no data is in the file,
    or the file is not present, it returns an empty list.
    '''
    try: # load list
        with open(filename, 'rt', encoding='utf8') as csvfile:
            csvfile = reader(csvfile)
            next(csvfile)
            for line in csvfile:
                try: filter_strings.append(line[0])
                except: print('Warning: line', str(file_reader.line_num) + ',', str(e) + '.')
    except: filter_strings = []
    return filter_strings

def normalize_dict(dict_str_int_wordcount):
    '''
    Normalize the dictionary with the word count.
    Normalizing, in this function, is give the most
    recurring word the value 100 and give
    all the other values proportional to it.
    '''
    max_elem = max(dict_str_int_wordcount.values())

    for key, value in dict_str_int_wordcount.items():
        normalized_val = float((100 * value)/max_elem) # int((100 * value)

        if normalized_val < 1: # == 0
            normalized_val = 1

        dict_str_int_wordcount[key]= normalized_val

    return dict_str_int_wordcount

def read_line(line, columns):
    '''
    Returns line in a dictionary in column keys.
    '''
    data = {}
    for column in columns:
        data[column] = line[columns[column]]
    return data

def split_list(iterable, chunksize=100):
    '''
    Split an array in iterables of N items.
    '''
    for i,c in enumerate(iterable[::chunksize]):
        yield iterable[i*chunksize:(i+1)*chunksize]

def str_from_list(lst, separator=', '):
    '''
    Return list as string.
    '''
    s = ''
    if isinstance(lst, list):
        for i in range(len(lst)):
            s = s + str(lst[i]) + (separator if i + 1 != len(lst) else '')
        return s
    else: return str(lst)

def str_from_num(number, decimal=2):
    '''
    Return the given int or float number with
    only 2 decimals by default and in string format.
    '''
    if isinstance(number, int):
        return str(number)

    elif isinstance(number, float):
        return str("%0.2f" % number).replace('.'+('0'*decimal),'')

    else: # string fallback
        s = str(number).split('.')
        try: s = float(s[0] + ('.'+ s[1][:decimal] if len(s)>1 else ''))
        except: return s[0]
        else: return str("%0.2f" % s).replace('.'+('0'*decimal),'')

def str_pct(num):
    '''
    Return the given number with
    only 2 decimals and a "%" appended.
    '''
    return(str("%0.2f" % num + "%"))

def str_to_list(string, separator=','):
    '''
    Return string as list.
    '''
    s = str(string).replace(separator+' ', separator)\
                   .replace('"', '')\
                   .replace('\'', '')\
                   .replace('\n', '')\
                   .replace('\r', '')
    return s.split(separator) if s else []

def time_to_print(current, mark=100000, msg='Read %n lines.\n', n='%n'):
    '''
    Return current line count and print total
    lines read when stop number is reached.
    '''
    if (current/mark).is_integer():
        print(msg.replace(n,str(current)), end='')