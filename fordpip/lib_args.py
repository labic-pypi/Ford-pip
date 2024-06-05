#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains a dictionary of arguments to parse,
which is loaded from "lib_config.py" and "lib_gooey.py" files.
'''

from argparse import ArgumentParser # RawTextHelpFormatter
from csv import QUOTE_MINIMAL, QUOTE_ALL, QUOTE_NONE
from os import environ

from .lib_ford import __version__
from .lib_input import list_from_list
from lang.english import CHOICES as CHOICES_ARGS

LANG = environ.get("FORD_LANGUAGE", "english")
LOGGING = environ.get("FORD_LOGGING", True)

if LANG == 'english':
    from lang.english import CHOICES
elif LANG == 'portuguese':
    from lang.portuguese import CHOICES

ARGS = {
'main': [['twitter', CHOICES['twitter']],
         ['facebook', CHOICES['facebook']],
         ['youtube', CHOICES['youtube']],
         ['images', CHOICES['images']],
         ['parse', CHOICES['parse']],
         ['tools', CHOICES['tools']],
         ['configure', CHOICES['configure']]],
'configure': [['install', CHOICES['install']],
              ['update', CHOICES['update']],
              ['wiki', CHOICES['wiki']],
              ['clean', CHOICES['clean']],
              ['uninstall', CHOICES['uninstall']]],
'twitter': [['collect', CHOICES['twitter_collect']],
            ['stream', CHOICES['tweepy_stream']],
            ['trending', CHOICES['trending_topics']],
            ['replies', CHOICES['twitter_replies']],
            ['scrap', CHOICES['twitter_scrap']]],
'twitter_data': [['tweets', CHOICES['tweets']],
                 ['timelines', CHOICES['timelines']],
                 ['ids', CHOICES['ids']],
                 #['id', CHOICES['id']],
                 ['retweeters', CHOICES['retweeters']],
                 ['retweets', CHOICES['retweets']],
                 ['users', CHOICES['users']],
                 #['user', CHOICES['user']],
                 ['friends', CHOICES['friends']],
                 ['followers', CHOICES['followers']]],
'facebook': [['feeds', CHOICES['facebook']]],
'facebook_data': [['feeds', CHOICES['feeds']],
                  ['pages', CHOICES['pages']],
                  ['posts', CHOICES['posts']],
                  ['shared', CHOICES['shared']],
                  ['comments', CHOICES['comments']],
                  ['members', CHOICES['members']],
                  ['search', CHOICES['search']]],
'facebook_format': [['advanced', CHOICES['advanced']],
                    ['classic', CHOICES['classic']],
                    ['reactions', CHOICES['reactions']],
                    ['basic', CHOICES['basic']],
                    ['split', CHOICES['split']]],
'youtube': [['youtube_search', CHOICES['youtube_search']],
            ['youtube_search_bychannel', CHOICES['youtube_search_bychannel']],
            ['youtube_comments', CHOICES['youtube_comments']],
            ['youtube_transcriptions', CHOICES['youtube_transcriptions']],
            ['youtube_thumbnails', CHOICES['youtube_thumbnails']],
            ['youtube_videos', CHOICES['youtube_videos']],
            ['youtube_parse', CHOICES['parse']]
            # ['youtube_help', CHOICES['youtube_help']]
],
'parse': [['tweets', CHOICES['twitter_parse']],
          ['tweets_ec', CHOICES['twitter_ec_parse']],
          ['tiktok_ec', CHOICES['tiktok_ec_parse']],
          ['facebook', CHOICES['facebook_parse']],
          ['crowdtangle', CHOICES['crowdtangle_parse']],
          ['exportcomments', CHOICES['exportcomments_parse']],
          ['instagram_parse', CHOICES['instagram_parse']],
          ['ngrams', CHOICES['ngrams']],
          ['kwic', CHOICES['kwic']],
          ['wordgraph', CHOICES['wordgraph']],
          ['wordgraph_tweets', CHOICES['wordgraph_tweets']],
          ['timeline', CHOICES['timeline']],
          ['wordsuite', CHOICES['wordsuite']],
          ['wordcloud', CHOICES['wordcloud']],
          ['categories', CHOICES['categorize']],
          ['categories_js', CHOICES['categorize_js']],
          ['mandala', CHOICES['mandala']],
          ['linkwords', CHOICES['linkwords']],
          ['tweetgraph', CHOICES['tweetgraph']],
          ['parsetangle', CHOICES['parsetangle']]],
'images': [['cluster_clip', CHOICES['cluster_clip']],
	   ['crawler', CHOICES['image_crawler']],
           ['crawler_v2', CHOICES['image_crawler_v2']],
           ['colors', CHOICES['image_colors']],
           ['imagegraphs', CHOICES['image_graphs']],
           ['imagepairs', CHOICES['image_pairs']],
           ['split_datasets', CHOICES['split_datasets']]],
'tools': [['fix', CHOICES['fix']],
          ['filter', CHOICES['filter']],
          ['randomize', CHOICES['randomize']],
          ['merge', CHOICES['merge']],
          ['merge_sheets', CHOICES['merge_sheets']],
          ['nulls', CHOICES['null_bytes']],
          ['split', CHOICES['split']],
          ['urls', CHOICES['urls']],
          ['convert', CHOICES['convert']],
          ['length', CHOICES['length']],
          ['filter_cluster', CHOICES['filter_cluster']]],
'time_format': [['%d/%m/%Y', CHOICES['%d/%m/%Y'], CHOICES_ARGS['%d/%m/%Y']],
                ['%d/%m/%Y %H', CHOICES['%d/%m/%Y %H'], CHOICES_ARGS['%d/%m/%Y %H']],
                ['%d/%m/%Y %H:%M', CHOICES['%d/%m/%Y %H:%M'], CHOICES_ARGS['%d/%m/%Y %H:%M']],
                ['%d/%m/%Y %H:%M:%S', CHOICES['%d/%m/%Y %H:%M:%S'], CHOICES_ARGS['%d/%m/%Y %H:%M:%S']],
                ['%m/%Y', CHOICES['%m/%Y'], CHOICES_ARGS['%m/%Y']],
                ['%Y', CHOICES['%Y'], CHOICES_ARGS['%Y']]],
'quote_format': [[QUOTE_MINIMAL, CHOICES[QUOTE_MINIMAL], CHOICES_ARGS[QUOTE_MINIMAL]],
                 [QUOTE_ALL, CHOICES[QUOTE_ALL], CHOICES_ARGS[QUOTE_ALL]],
                 [QUOTE_NONE, CHOICES[QUOTE_NONE], CHOICES_ARGS[QUOTE_NONE]]],
'filter_type': [['text', CHOICES['text']],
                ['numeric', CHOICES['numeric']],
                ['date', CHOICES['date']],
                ['cut', CHOICES['cut']]]}

def args_parser():
    '''
    Read arguments given as input on execution.
    '''
    parser = ArgumentParser(add_help=False)

    # load choices lists
    choices_main = list_from_list(ARGS['main'])
    choices_configure = list_from_list(ARGS['configure'])
    choices_twitter = list_from_list(ARGS['twitter'])
    choices_facebook = list_from_list(ARGS['facebook'])
    choices_images = list_from_list(ARGS['images'])
    choices_parse = list_from_list(ARGS['parse'])
    choices_tools = list_from_list(ARGS['tools'])
    choices_twitter_data = list_from_list(ARGS['twitter_data'])
    choices_facebook_data = list_from_list(ARGS['facebook_data'])
    choices_facebook_format = list_from_list(ARGS['facebook_format'])
    choices_time_format = list_from_list(ARGS['time_format'], n=2)
    choices_quote_format = list_from_list(ARGS['quote_format'], n=2)
    choices_exec = choices_main + choices_twitter + choices_facebook +\
        choices_images + choices_parse + choices_tools + choices_configure

    # main arguments
    parser.add_argument('main', nargs='?', choices=choices_exec, default=None)
    parser.add_argument('--classic', dest='classic', action='store_true', default=False)
    parser.add_argument('--version', action='version', version=__version__, help='')
    parser.add_argument('--help', '-h', action='store_true', dest='help')
    # Facebook and Twitter mining options
    parser.add_argument('-t', '--twitter-data', nargs='?', choices=choices_twitter_data, const=choices_twitter_data[0], default=choices_twitter_data[0])
    parser.add_argument('-f', '--facebook-data', nargs='?', choices=choices_facebook_data, const=choices_facebook_data[0], default=choices_facebook_data[0])
    parser.add_argument('-F', '--facebook-format', nargs='?', choices=choices_facebook_format, const=choices_facebook_format[0], default=choices_facebook_format[0])
    # more options and modifiers
    parser.add_argument('-a', '--all-folders', dest='merge_subfolders', action='store_true')
    parser.add_argument('-c', '-cc', '--columns', action='store')
    parser.add_argument('-cs', '--case-sensitive', action='store_true')
    parser.add_argument('-d', '--days', dest='max_days', action='store')
    parser.add_argument('-e', '--exclude', dest='exclude_words', action='store', default=[])
    parser.add_argument('-g', '--geocodes', '--geonames', action='store')
    parser.add_argument('-i', '--input', action='store')
    parser.add_argument('-l', '--language', action='store')
    parser.add_argument('-max', '--maximum', action='store')
    parser.add_argument('-min', '--minimum', action='store')
    parser.add_argument('-n', '--number', dest='max_number', action='store')
    parser.add_argument('-o', '--output', action='store')
    parser.add_argument('-q', '--quiet', action='store_true')
    parser.add_argument('-r', '--reverse', action='store_true')
    parser.add_argument('-s', '--strings', dest='text_strings', action='store')
    parser.add_argument('-uid', '-uids', '--user-ids', '--userids', dest='twitter_user_id', action='store_true')
    parser.add_argument('-u', '--utc', dest='time_zone', action='store_const', const=0)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-w', '--words', dest='max_words', action='store', default=15)
    parser.add_argument('-W', '--word-wrap', '--wordwrap', action='store_true')
    parser.add_argument('-y', '--force', action='store_true')
    parser.add_argument('-z', '--time-zone', '--timezone', dest='time_zone', action='store', default=None)
    parser.add_argument('--insert', dest='insert_words', action='store', default=[])
    parser.add_argument('--quick-parse', dest='quick_parse', action='store_true')
    # categorize only arguments
    parser.add_argument('-cf', action='store') # file
    parser.add_argument('-c-ms', action='store') # min size
    parser.add_argument('-c-tf', action='store') # text field
    parser.add_argument('-c-df', action='store') # date field
    parser.add_argument('-c-idpf', action='store') # id post field
    parser.add_argument('-c-lf', action='store') # like field
    parser.add_argument('-c-fq', action='store') # file quote
    parser.add_argument('-mfc', action='store_true') # multiple files categorize
    parser.add_argument('-ejson', action='store_true') # export json
    # text delimiting and parsing
    parser.add_argument('--consider', dest='consider', action='store', default=None)
    parser.add_argument('--delimiter', dest='output_delimiter', action='store')
    parser.add_argument('--time', dest='time_format', nargs='?', choices=choices_time_format, const=choices_time_format[0], default=choices_time_format[0])
    parser.add_argument('--quote', dest='quote_format', nargs='?', choices=choices_quote_format, const=choices_quote_format[0], default=choices_quote_format[0])
    # Twitter streaming options
    parser.add_argument('--ats-only', dest='stream_ats', action='store_true', default=None)
    parser.add_argument('--rts-only', dest='stream_rts', action='store_true', default=None)
    parser.add_argument('--no-ats', dest='stream_ats', action='store_false', default=None)
    parser.add_argument('--no-rts', dest='stream_rts', action='store_false', default=None)
    parser.add_argument('--no-gephi', dest='gephi', action='store_false')
    parser.add_argument('--port', action='store', default='8181')
    # image mining and parsing options
    parser.add_argument('--input-aisi', action='store', default='exp.txt')
    parser.add_argument('--input-imgj', action='store', default='Tempo_RT.txt')
    parser.add_argument('--column-users', action='store', default='from_user')
    parser.add_argument('--column-urls', action='store', default='media_url')
    # Mandala viz options
    parser.add_argument('--concur', dest='concur_words', action='store', default=2)
    parser.add_argument('--levels', '--depth', dest='depth_words', action='store', default=5)
    # file fixing
    parser.add_argument('--encode', action='store', default='utf8')
    parser.add_argument('--no-length', dest='fix_line_length', action='store_false')
    parser.add_argument('--no-unique', dest='fix_duplicate_lines', action='store_false')
    parser.add_argument('--no-null-bytes', dest='fix_null_bytes', action='store_false')
    # general arguments
    parser.add_argument('--editor', dest='editor', action='store')
    parser.add_argument('--log', dest='log', action='store', default=LOGGING)
    parser.add_argument('--no-log', dest='log', action='store_false')
    parser.add_argument('--max-memory', dest='max_memory', action='store', default=1024)
    # return as dictionary
    return vars(parser.parse_args())
