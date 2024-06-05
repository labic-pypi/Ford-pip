#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains the functions for setting the
script arguments on execution using the argparse library.

If the quiet modifier (-q or --quiet) is not set, the
script will ask the user for more recommended settings.
'''

# import Python libraries

from os import environ, getcwd, listdir, remove
from os.path import abspath, basename, dirname, isdir, isfile, realpath, splitext
from shutil import move
from sys import argv

# import script libraries

from .lib_args import ARGS, args_parser
from .lib_input import get_file_header, list_from_list
from .lib_input import str_from_list, str_to_list
from .lib_sys import file_error, less, list_path, read
from .lib_text import remove_latin_accents

# import default user configuration
CLASSIC = environ.get("FORD_CLASSIC", True)
LANG = environ.get("FORD_LANGUAGE", "english")

# load text for arguments based on language
from lang.english import CHOICES, QUERY
if LANG == 'portuguese':
    from lang.portuguese import CHOICES, QUERY

# load graphic user interface if classic unset

if not CLASSIC: # workaround for Gooey and CLI compability
    CLASSIC = (len(argv)>1 and '--ignore-gooey' not in argv)

if not CLASSIC: # check if GUI library is installed
    try: from .lib_gooey import gooey_parser
    except ImportError: GUI = False # <== raise this if bug-hunting!
    else: GUI = True
else: GUI = False

def config_args(args={}, skip_parse=False):
    '''
    Configure arguments on execution time.
    '''
    # set default arguments
    args['editor'] = None   # get default from system
    args['log'] = True      # default output to "log.txt"
    args['quiet'] = False   # No to All questions
    args['force'] = True    # Yes to All questions
    args['verbose'] = False # show detailed output
    args['time_zone'] = 0   # UTC

    # add required path dirs
    args['path_script'] = dirname(realpath(argv[0]))
    args['path_input'] = getcwd() # current working directory

    # set default parse choices
    args['quote_format'] = ARGS['quote_format'][0]
    args['time_format'] = ARGS['time_format'][0]

    # remove leftover configuration files
    [remove(f"{args['path_script']}/{f}") for f in listdir(args["path_script"]) if f.lower().startswith("config")]

    # skip argument parsing
    if skip_parse: pass

    # graphic user interface
    elif GUI and not CLASSIC:
        args['GUI'] = True
        # read input arguments
        parsed_args = gooey_parser() # <== loads graphic interface!

    else: # command line interface
        args['GUI'] = False
        # read and update input arguments
        parsed_args = args_parser()
        args.update(parsed_args)
        # ask common arguments
        if not args['quiet'] and not args['help']:
            args = args_ask(args) # <== loads command line interface!
    # replace keys with values and
    # add parsed arguments to dict while
    # maintaining CLI/GUI compability
    for a in sorted(parsed_args.keys()):
        # main argument stored in "command" by gooey
        if a == 'command':
            continue # skip
        # argument value
        choice = args[a]
        # get choice value from dictionary
        # eg: "days" => "%d/%m/%Y" (time_format)
        if a in ARGS.keys():
            for k in ARGS[a]:
                if k[1] == choice\
                or (len(k)==3 and k[2] == choice):
                    choice = k[0]
        # set main argument
        if a in list_from_list(ARGS['main'], n=0):
            args['main'] = choice
        # set argument for input name
        elif (a == 'input_folder'\
        and not parsed_args['input']):
            args['input'] = choice
        elif a in ('input', 'text_strings', 'geocodes', 'log', 'exclude_words')\
        and choice and isfile(choice):
          args[a] = abspath(choice)
        # if default value
        else:
          args[a] = choice

    # compability workarounds
    if 'input' not in args:
        args['input'] = None
    if 'output' not in args:
        args['output'] = None
    if 'output_path' not in args:
        args['output_path'] = remove_latin_accents(splitext(basename(str(args['input'])))[0])[:40]
    # set helper
    if args['help'] and not args['main']:
        args['main'] = 'help'
    # add wordgraph default columns
    if args['main'] == 'wordgraph'\
    and args['columns']:
        a = str_to_list(args['columns'])
        a.append('id')
        a.append('time')
        args['columns'] = str_from_list(list(set(a)))
    # set output logging default behavior
    """ if not isinstance(args['log'], str)\
    and args['main'] in list_from_list(ARGS['configure']):
        args['log'] = False """

    return args

def args_ask(args):
    '''
    Ask user for common aguments if none given.
    '''
    # set valid main arguments
    valid_args = []
    for k in list_from_list(ARGS['main'], n=0):
        for a in ARGS[k]:
            valid_args.append(a[0])

    # set arguments requiring input file
    file_args = []
    for k in ['images', 'parse', 'tools']:
        for a in ARGS[k]:
            if a[0] not in ['filter_cluster']:
                file_args.append(a[0])

    # set arguments requiring input folder
    folder_args = ['merge', 'merge_sheets', 'colors', 'split_datasets']

    # action to execute
    if not args['main']:
        args['main'] = read(QUERY['q']+QUERY['main'],
            opt=list_from_list(ARGS['main']),
            opt_desc=list_from_list(ARGS['main'], n=1))

    # choose twitter/facebook/images/text/files
    if args['main'] in ARGS.keys():
        # automatically choose if one option
        if len(ARGS[args['main']]) == 1:
            args['main'] = ARGS[args['main']][0][0]
        else: # ask which among groups of options
            args['main'] = read(QUERY['q']+QUERY['option'],
                opt=list_from_list(ARGS[args['main']]),
                opt_desc=list_from_list(ARGS[args['main']], n=1))

    # set input folder name
    if args['main'] in folder_args:
        # ask user; optional
        if not args['input']:
            args['input'] = read(QUERY['q']+QUERY['folder'],
                                 default='.',
                                 optional=True)
        # default to current path
        if args['input'] == '':
            args['input'] = '.'
        # raise error if not found
        elif not isdir(args['input'])\
        and not (args['input'] == '*' and args['main'] == 'merge'):
            file_error(args['input'])

    # set input files from AISI/ImageJ
    elif args['main'] == 'pairs':
        # set default
        if isfile('exp.txt'):
            file_aisi = 'exp.txt'
            print('AISI output file set as \'exp.txt\'.')
        else: # or ask user
            file_aisi = read(QUERY['q']+QUERY['file_aisi'])
        # set default
        if isfile('Tempo_RT.txt'):
            file_imgj = 'Tempo_RT.txt'
            print('ImageJ output file set as \'Tempo_RT.txt\'.')
        else: # or ask user
            file_imgj = read(QUERY['q']+QUERY['file_imgj'])

    # set input file or folder name
    elif args['main'] == 'wordgraph_tweets':
        args['input'] = read(QUERY['q']+'input file or folder (leave blank for current folder)',
                                 default='.',
                                 #opt=list_path('.', ignore=['cfg','log']),
                                 opt_hidden=list_path('.', folders=True, ext=['csv', 'xlsx']))

    # set input file name
    elif args['main'] in file_args\
    and args['facebook_data'] != 'search':
        # ask user; required
        if not args['input']:
            args['input'] = read(QUERY['q']+QUERY['file'],
                                 #opt=list_path('.', ignore=['cfg','log']),
                                 opt_hidden=list_path('.', ignore=['cfg', 'log']))
        # raise error if not found
        if not args['input'] or not (isfile(args['input']) or isdir(args['input'])):
            file_error(args['input'])

    # set input type
    if args['main'] in QUERY.keys():
        # Facebook arguments before query input
        if args['main'] == 'feeds':
            # ask query type if default
            if args['facebook_data'] == 'feeds':
                args['facebook_data'] = read(QUERY['q']+QUERY['query_type'],
                                             opt=list_from_list(ARGS['facebook_data']),
                                             opt_desc=list_from_list(ARGS['facebook_data'],n=1))
            # choose output format
            if args['facebook_data'] == 'feeds':
                args['facebook_format'] = read(QUERY['q']+QUERY['output_format'],
                                               opt=list_from_list(ARGS['facebook_format']),
                                               opt_desc=list_from_list(ARGS['facebook_format'],n=1))
                # minimum capture date
                if not args['minimum']:
                    args['minimum'] = read(QUERY['q']+QUERY['min_date'])
                # maxium capture date
                if not args['maximum']:
                    args['maximum'] = read(QUERY['q']+QUERY['max_date'])

        # Twitter arguments before query input
        elif args['main'] == 'collect' and args['twitter_data'] == 'tweets':
            args['twitter_data'] = read(QUERY['q']+QUERY['query_type'],
                                        opt=list_from_list(ARGS['twitter_data']),
                                        opt_desc=list_from_list(ARGS['twitter_data'],n=1),
                                        default='tweets')

        # ask query input
        if not args['input']\
        and args['facebook_data'] != 'search':
            while True: # in a loop
                args['input'] = read(QUERY['q']+QUERY[args['main']],
                                    #  opt_hidden=list_path('.', ignore=['cfg', 'log']),
                                     optional=True\
                                              if args['main'] == 'trending_topics'\
                                              or args['twitter_data'] == 'tweets'\
                                              or args['facebook_data'] == 'pages'\
                                              else False)
                break
                """ # show help file
                if args['input'] == '?' and '?' in QUERY[args['main']]:
                    help_file = 'README.md' if LANG == 'english' else 'LEIAME.md'
                    less(dirname(realpath(argv[0]))+'/'+help_file, line='+126') # Twitter operators
                else: break """

        # check if file exists when required
        if args['input'] and 'file name' in QUERY[args['main']] and not isfile(args['input']):
            file_error(args['input']) if args['facebook_data'] != 'pages' else None

        # Twitter arguments after query input
        if args['main'] == 'collect' and args['twitter_data'] == 'tweets':
            if not args['max_days']:
                args['max_days'] = read(QUERY['q']+QUERY['max_days'], optional=True)
            if not args['language']:
                args['language'] = read(QUERY['q']+QUERY['language'], optional=True)
            if not args['geocodes']:
                optional = True if args['twitter_data'] == 'tweets' and args['input'] else False
                # ask as optional if querying tweets by input keywords
                args['geocodes'] = read(QUERY['q']+QUERY['geocodes'], optional=optional)

    # ask to merge subfolders
    if args['main'] == 'merge':
        args['merge_subfolders'] = read(QUERY['merge'], confirm=True)
        args["text_strings"] = read(QUERY['q']+QUERY['text_merge'], optional=True, default=None)

    # set filter input
    filter_args = ['tweets', 'facebook', 'mandala', 'wordgraph', 'wordcloud', 'wordsuite']

    if not any(args[i] for i in ['columns', 'minimum', 'maximum', 'text_strings'])\
    and args['main'] == 'filter' or (args['main'] in filter_args and read(QUERY['filter'], confirm=True)):

        # set data to filter
        option = read(QUERY['q']+QUERY['filter_type'],
                      opt=list_from_list(ARGS['filter_type']),
                      opt_desc=list_from_list(ARGS['filter_type'],n=1))

        # set columns to filter
        if not args['columns'] and not (option == 'text' and args['text_strings']):
            optional = True if option == 'text' else False
            # ask as optional if filtering by text strings
            args['columns'] = read(QUERY['q']+QUERY['columns']+' ('+(QUERY['optional']+', ' if option == 'text' else '')+QUERY['question_for_list']+')',
                                          opt_hidden=get_file_header(args['input'], lowcase=False),
                                          optional=optional)

        # set date or numeric interval
        if all(not args[i] for i in ['minimum', 'maximum']):
            if option == 'date':
                args['minimum'] = read(QUERY['q']+QUERY['min_date'], optional=True)
                args['maximum'] = read(QUERY['q']+QUERY['max_date'], optional=True if args['minimum'] else False)
            elif option == 'numeric':
                args['minimum'] = read(QUERY['q']+QUERY['min_filter'], optional=True)
                args['maximum'] = read(QUERY['q']+QUERY['max_filter'], optional=True if args['minimum'] else False)

        # set text strings to filter
        if option == 'text' and not args['text_strings']:
            args['text_strings'] = read(QUERY['q']+QUERY['text_filter'])

    # set Twitter post-collect actions
    if args['main'] == 'collect'\
    and args['twitter_data'] in ('tweets', 'timelines', 'ids', 'retweets'):
        # defaults
        args['twitter_mine_and_scrap'] = False
        args['twitter_mine_and_parse'] = False
        args['twitter_mine_images'] = False
        # scrap @-messages
        if args['force'] or read(QUERY['twitter_mine_and_scrap'], confirm=True):
            args['twitter_mine_and_scrap'] = True
        # parse tweets
        if args['force'] or read(QUERY['twitter_mine_and_parse'], confirm=True):
            args['twitter_mine_and_parse'] = True
        # crawl images
        if args['force'] or read(QUERY['twitter_mine_images'], confirm=True):
            args['twitter_mine_images'] = True

    # set Facebook post-collect actions
    if args['main'] == 'feeds'\
    and args['facebook_data'] in ('feeds', 'individual', 'posts'):
        # defaults
        args['facebook_mine_and_parse'] = False
        args['facebook_mine_images'] = False
        # parse dataset
        if args['force'] or read(QUERY['facebook_mine_and_parse'], confirm=True):
            args['facebook_mine_and_parse'] = True
        # crawl images
        if args['force'] or read(QUERY['facebook_mine_images'], confirm=True):
            args['facebook_mine_images'] = True

    if args['main'] == 'categories':
        filters_path = abspath(args['path_script']+'/lib/script_categorias/termos')
        # get list of files available
        list_of_files = list_path(args['path_input'], ignore=['cfg','log']) # list of input files
        list_of_filters = list_path(filters_path, absolute=True) # list of filters
        # default filters names
        name_of_filters = []
        for n in list_path(filters_path, names=True):
            name_of_filters.append(n+'*')
        # categories data file
        if not args.get('categorize_file', None):
            args['categorize_file'] = read(QUERY['q']+QUERY['categorize_file'],
                  opt=list_of_filters+list_of_files,
                  opt_hidden=name_of_filters+list_of_files)
        # text columns in file
        if not args['columns']:
            args['columns'] = read(QUERY['q']+QUERY['columns']+' ('+QUERY['optional']+", "+QUERY['question_for_list']+')',
                  default=None,
                  opt_hidden=get_file_header(args['input'], lowcase=False),
                  optional=True)

    if args['main'] == 'categories_js':
        filters_path = abspath(args['path_script']+'/lib/script_categorias/termos')
        # get list of files available
        list_of_files = list_path(args['path_input'], ignore=['cfg','log']) # list of input files
        list_of_filters = list_path(filters_path, absolute=True) # list of filters
        # default filters names
        name_of_filters = []
        for n in list_path(filters_path, names=True):
            name_of_filters.append(n+'*')
        # categories data file
        if not args.get('categorize_file', None):
            args['categorize_file'] = read(QUERY['q']+QUERY['categorize_file'],
                  opt=list_of_filters+list_of_files,
                  opt_hidden=name_of_filters+list_of_files)
        # categories columns in file
        if not args['columns']:
            args['columns'] = read(QUERY['q']+QUERY['categorize_columns'],
                  default='B,C')

    if args['main'] == 'wordgraph_tweets':
        args['text_strings'] = read(QUERY['q']+"text to filter (optional, e.g.: 'rio grande do sul, rio grande do norte')", optional=True)
        args['insert_words'] = read(QUERY['q']+"words to INSERT (optional, e.g.: 'word, this term')", optional=True)
        args['exclude_words'] = read(QUERY['q']+"words to EXCLUDE (optional, e.g.: 'word, another term')", optional=True)

    return args
