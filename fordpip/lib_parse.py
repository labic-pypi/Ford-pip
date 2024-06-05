
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Sift data and generate statistics and graphs of Facebook and Twitter datasets.

Input data can be optionally filtered prior to parsing, and tweet locations
further geocoded with a gazetteer: <http://download.geonames.org/export/dump/>.

For text analysis, a list of 4190 stopwords in 10 languages is provided and is
modifiable by editing the "lib_stopwords.py" file located in "src" folder.

Merge path and color parsing both accept the "." wildcard for current directory.
'''

import sys

from os import chdir
from os.path import abspath, basename, isfile
from shutil import copy
from subprocess import call

from .lib_excel import csv_from_excel
from .lib_input import filename_append, get_file_header
from .lib_sys import Logger, mkpath, read

from .categorize import Categorize
from .categorize_js import categorize as categorize_js
from .image_colors import image_colors
from .image_graphs import image_graphs
from .image_pairs import image_pairs
from .image_split import split_image_datasets
from .file_filter_cluster import file_filter_cluster
from .file_filter import file_filter
from .file_fix import file_fix, fix_null_bytes, drop_lines
from .file_merge import file_merge, sheets_merge
from .file_split import file_split
from .lib_length import csv_field_length
from .lib_kwic import kwic_parse
from .lib_ngrams import ngrams_parse
from .mandala import mandala as Mandala
from .parse_crowdtangle import parse_crowdtangle
from .parsetangle import parsetangle
from .parse_comments import ParseComments
from .parse_facebook import parse_facebook
from .parse_tweets import parse_tweets, parse_tweets_ec
from .parse_tiktok import parse_tiktok_ec
from .randomize import randomize as Randomize
from .twitter_convert import convert_json, convert_pickle
from .urls_expand import urls_expand
from .word_cloud import wordcloud as Wordcloud
from .word_graph import wordgraph as Wordgraph
from .word_graph_tweets import wordgraph_tweets as Wordgraph_Tweets
from .word_links import linkwords as Linkwords
from .word_suite import wordsuite as Wordsuite
from .word_timeline import timeline as Timeline

# twitter functions #

def tweets(args):
    '''
    Parse tweets output dataset from flashback,
    YourTwapperKeeper or pygephi_graphstreaming scripts.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    parse_tweets(input_name=args['input'],
        quoting=args['quote_format'],
        time_string=args['time_format'],
        time_zone=args['time_zone'],
        geonames=args['geocodes'])
    # copy README file
    copy(abspath(args['path_script']+'/man/parse_tweets.xlsx'), "LEIA-ME.xlsx")

def tweetgraph(args):
    '''
    Call tweetgraph script to generate graphs.
    Requires R-igraph package installed:
    '''
    script = abspath(args['path_script'] + '/lib/tweetgraph/tweetgraph3.1.r')
    # call external script
    print('Calling Tweetgraph script...')
    call(['Rscript', script, args['input']])

# twitter (exportcomments) functions #
def tweets_ec(args):
    '''
    Parse tweets from ExportComments
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
        # drop first 6 lines
        drop_lines(input_name=args['input'], drop_lines=6)
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    parse_tweets_ec(input_name=args['input'],
        quoting=args['quote_format'],
        time_string=args['time_format'],
        time_zone=args['time_zone'],
        geonames=args['geocodes'])
    # copy README file
    copy(abspath(args['path_script']+'/man/parse_tweets.xlsx'), "LEIA-ME.xlsx")

# tiktok functions #
def tiktok_ec(args):
    '''
    Parse tweets from ExportComments
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
        # drop first 6 lines
        drop_lines(input_name=args['input'], drop_lines=6)
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    parse_tiktok_ec(input_name=args['input'],
        quoting=args['quote_format'],
        time_string=args['time_format'],
        time_zone=args['time_zone'],
        geonames=args['geocodes'])
    # copy README file
    copy(abspath(args['path_script']+'/man/parse_tweets.xlsx'), "LEIA-ME.xlsx")


# facebook functions #

def facebook(args):
    '''
    Parse Facebook datasets from FacebookFeeds.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    parse_facebook(input_name=args['input'],
        quoting=args['quote_format'],
        time_string=args['time_format'],
        time_zone=args['time_zone'])
    # analyze comments in posts
    """ if isfile('comments.csv'):
        mkpath('COMMENTS', cd=True)
        netvizz_comments(input_name=args['input'],
                         quoting=args['quote_format'],
                         time_string=args['time_format'],
                         time_zone=args['time_zone']) """

# crowdtangle and exportcomments #

def crowdtangle(args):
    '''
    Analyze data from CrowdTangle.
    '''
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    parse_crowdtangle(input_name=args['input'])

def exportcomments(args):
    '''
    Analyze data from ExportComments.
    '''
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=False)
    ParseComments().parse_comments(
        input_name=args['input'],
        output_name=output_path,
        quick_parse=args['quick_parse'])

# image functions #

def colors(args):
    '''
    Analyze colors from images in a folder.
    '''
    image_colors(folder_name=args['input'])

def imagegraphs(args):
    '''
    Generate graphs from images in dataset.
    '''
    Image_graphs(file_name=args['input'])

def imagepairs(args):
    '''
    Pair images from AISI and ImageJ output files.
    '''
    Image_pairs(file_aisi=args['input_aisi'],
        file_imgj=args['input_imgj'])

def split_datasets(args):
    '''
    Split collected images from diferent datasets
    '''
    print('aqui')
    split_image_datasets(args)

# text and semantics #

def linkwords(args):
    '''
    Call LinkWords script to analyze word occurrences.
    Requires X and Java Runtime Environment (JRE) installed.
    '''
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    script = args['path_script'] + '/lib/LinkWords/LinkWords.jar'
    Linkwords(input_name=args['input'],
        script=script)

def mandala(args):
    '''
    Call Mandala script to analyze word concurrences.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    script_path = args['path_script'] + '/lib/mandala'
    Mandala(input_name=args['input'],
        exclude_words=args['exclude_words'],
        max_words=int(args['max_words'])\
            if args['max_words']\
            else None,
        max_height=int(args['concur_words'])\
            if args['concur_words']\
            else None,
        max_depth=int(args['depth_words'])\
            if args['depth_words']\
            else None,
        path_script=script_path)

def wordcloud(args):
    '''
    Generate word cloud from text file.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    Wordcloud(input_name=args['input'])

def timeline(args):
    '''
    Generate daily word graphs and word clouds.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    Timeline(input_name=args['input'],
        include_words=args['text_strings'],
        exclude_words=args['exclude_words'],
        max_words=int(args['max_words'])\
            if args['max_words']\
            else None,
        separator=',')

def wordgraph(args):
    '''
    Generate daily word graphs and word clouds.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    Wordgraph(input_name=args['input'],
        include_words=args['text_strings'],
        exclude_words=args['exclude_words'],
        max_words=int(args['max_words'])\
            if args['max_words']\
            else None,
        separator=',')

def wordgraph_tweets(args):
    '''
    Generate Twitter/ExportComments word graph.
    '''
    args['input'] = abspath(args['input'])
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    # if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
    #     output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
    #     csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
    #     args['input'] = output_file
    # fix null bytes to avoid errors
    # if args['fix_null_bytes']:
    #     output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
    #     fix_null_bytes(input_name=args['input'],
    #         output_name=output_file)
    #     args['input'] = output_file
    # call script function
    Wordgraph_Tweets(path=args['input'],
        words=args['text_strings'],
        insert_words=args['insert_words'],
        exclude_words=args['exclude_words'],
        skiprows=args['max_number'] if args['max_number'] is not None else 6,
    )

def wordsuite(args):
    '''
    Generate word analysis suite from text file.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # filter dataset prior to analysis
    if any(args[a] for a in ['columns', 'minimum', 'maximum', 'text_strings']):
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            minimum=args['minimum'],
            maximum=args['maximum'],
            words=args['text_strings'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()
    # call script function
    Wordsuite(input_name=args['input'],
        top_words=args['text_strings'],
        exclude_words=args['exclude_words'],
        max_words=int(args['max_words'])\
            if args['max_words']\
            else None,
        interval=int(args['max_number'])\
            if args['max_number']\
            else 100)

# file tools #

def convert(args):
    '''
    Convert Excel, JSON streaming or pickle files to CSV format.
    '''
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        csv_from_excel(input_file=args['input'], quoting=args['quote_format'])
    elif args['input'].endswith('.json'):
        convert_json(input_file=args['input'])
    elif args['input'].endswith('.pickle'):
        convert_pickle(input_file=args['input'])
    else: print('Error: file extension must be JSON/pickle/xls/xlsx.')

def filter(args):
    '''
    Filter dataset by text, numbers or column fields.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    file_filter(input_name=args['input'],
        output_name=args['output'],
        output_delimiter=args['output_delimiter'],
        columns=args['columns'],
        minimum=args['minimum'],
        maximum=args['maximum'],
        words=args['text_strings'],
        case_sensitive=args['case_sensitive'],
        matches_all=args['force'],
        reverse=args['reverse'],
        unique_lines=args['fix_duplicate_lines'],
        word_wrap=args['word_wrap'],
        quoting=args['quote_format'],
        separator=',')

def fix(args):
    '''
    Repair datasets from null byte characters,
    uneven length lines and file encoding.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    file_fix(input_name=args['input'],
        output_name=args['output'],
        output_delimiter=args['output_delimiter'],
        unique_lines=args['fix_duplicate_lines'],
        fix_length=args['fix_line_length'],
        encoding=args['encode'],
        quoting=args['quote_format'])

def merge(args):
    '''
    Merge files in folder and subfolders.
    '''
    file_merge(input_name=args['input'],
        output_name=args['output'],
        file_include=args['text_strings'],
        file_exclude=args['exclude_words'],
        merge_subfolders=args['merge_subfolders'],
        separator=',')

def merge_sheets(args):
    '''
    Merge sheets from Excel files.
    '''
    sheets_merge(folder_name=args['input'],)

def filter_cluster(args):
    '''
    Filter dataset by actors from the same cluster.
    '''
    file_filter_cluster()


def nulls(args):
    '''
    Repair datasets from null byte characters,
    uneven length lines and file encoding.
    '''
    fix_null_bytes(input_name=args['input'],
        output_name=args['output'])

def split(args):
    '''
    Expand shortened URLs found in text file.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    # call script function
    file_split(input_name=args['input'],
        number_of_lines=args['max_number'])

def urls(args):
    '''
    Expand shortened URLs found in text file.
    '''
    # make new folder and change directory
    output_path = 'RESULTS ('+args['output_path']+')'
    mkpath(args['output'] if args['output'] else output_path, cd=True)
    # convert from excel to CSV format
    if any(args['input'].endswith(x) for x in ['.xls', '.xlsx']):
        output_file = abspath(basename(args['input']).replace('xlsx','xls').replace('xls','csv'))
        csv_from_excel(input_file=args['input'], output_file=output_file, quoting=args['quote_format'])
        args['input'] = output_file
    # fix null bytes to avoid errors
    if args['fix_null_bytes']:
        output_file = abspath(filename_append(basename(args['input']), '_NO_NULL'))
        fix_null_bytes(input_name=args['input'],
            output_name=output_file)
        args['input'] = output_file
    urls_expand(input_name=args['input'],
        output_name=args['output'],
        output_delimiter=args['output_delimiter'])

def categories(args):
    '''
    Advanced analysis of datasets using external filters.
    '''
    # call wrapper script
    Categorize().categorize(
        input_name=args['input'],
        categories=args['categorize_file'],
        case_sensitive=args['case_sensitive'],
        min_length=args['minimum'],
        text_columns=args['columns'],
        output_folder=True,
        xlabel="Porcentagem",
        ylabel="Categoria")

def categories_js(args):
    '''
    Advanced analysis of datasets using external filters (JavaScript).
    '''
    # set external script to call
    script = abspath(args['path_script'] + '/lib/script_categorias')
    # call wrapper script
    categorize_js(input_name=args['input'],
        cf=args['categorize_file'],
        cc=args['columns'],
        c_tf=args['c_tf'],
        c_df=args['c_df'],
        c_lf=args['c_lf'],
        c_idpf=args['c_idpf'],
        c_ms=args['c_ms'],
        output=args['output'],
        script_path=script)

def length(args):
    '''
    Cut lines based on field value length.
    '''
    if not args['columns']:
        args['columns'] = read('Please enter the column name (optional)',
                               opt_hidden=get_file_header(args['input'], lowcase=False),
                               optional=True)

    if not args['minimum']:
        args['minimum'] = read('Please enter the minimum length', optional=True)

    if not args['maximum']:
        args['maximum'] = read('Please enter the maximum length', optional=True)

    csv_field_length(args['input'],
        args['output'],
        args['columns'],
        int(args['maximum']) if args['maximum'] else None,
        int(args['minimum']) if args['minimum'] else None)

def ngrams(args):
    '''
    Quick KWIC analysis, plus n-grams from NLTK.
    '''
    if not args['columns']:
        args['columns'] = read('Please enter the column name or position (optional)',
                               opt_hidden=get_file_header(args['input'], lowcase=False),
                               optional=True)
    if not args['max_number']:
        args['max_number'] = read('Please enter the n-value (default: n=2)', optional=True)
    if not args['max_number']:
        args['max_number'] = 2
    if not args['text_strings']:
        args['text_strings'] = read('Please enter the keywords (optional)', optional=True)
    if not args['minimum']:
        args['minimum'] = 2

    if args['columns']:
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()

    ngrams_parse(args['input'],
        keywords=args['text_strings'] if args['text_strings'] else [],
        n_value=int(args['max_number']) if args['max_number'] else 2,
        min_len=int(args['minimum']) if args['minimum'] else 2)

def kwic(args):
    if not args['columns']:
        args['columns'] = read('Please enter the column name or position (optional)',
                               opt_hidden=get_file_header(args['input'], lowcase=False),
                               optional=True)

    if not args['max_number']:
        args['max_number'] = read('Please enter the KWIC size (default: 5)', optional=True)

    if not args['text_strings']:
        args['text_strings'] = read('Please enter the keywords (optional)', optional=True)

    if not args['text_strings']:
        args['maximum'] = read('Please enter the maximum number of keywords (optional, default: 3)', optional=True)

    if args['columns']:
        output_file = abspath(filename_append(basename(args['input']), '_FILTERED'))
        file_filter(input_name=args['input'],
            output_name=output_file,
            output_delimiter=args['output_delimiter'],
            columns=args['columns'],
            case_sensitive=args['case_sensitive'],
            matches_all=args['force'],
            reverse=args['reverse'],
            unique_lines=False,
            word_wrap=args['word_wrap'],
            quoting=args['quote_format'],
            separator=',')
        args['input'] = output_file; print()

    kwic_parse(args['input'],
        keywords=args['text_strings'] if args['text_strings'] else [],
        max_keywords=args['maximum'] if args['maximum'] else 3,
        size=args['max_number'] if args['max_number'] else 5)

def randomize(args):
    Randomize(args)
