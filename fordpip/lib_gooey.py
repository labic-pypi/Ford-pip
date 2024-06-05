#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains the function for setting the
Graphic User Interface using the python3-gooey library.

If the library fails to load or isn't at all installed,
the script will ask for recommended settings through CLI.
This behaviour can be forced with "--classic" on execution.

The GUI display language can be set to any supported
by Gooey, though the script options are only currently
available in portuguese and english so far.
'''

from gooey import Gooey, GooeyParser
from os import environ, getcwd
from os.path import abspath, dirname, realpath
from sys import argv
from time import time

from .lib_args import ARGS
from .lib_ford import __version__
from .lib_input import list_from_list
from .lib_time import datetime_from_timestamp, datetime_to_str, get_local_tz

LANG = environ.get("FORD_LANGUAGE", "english")

if LANG == 'english':
    from lang.english import HELP
elif LANG == 'portuguese':
    from lang.portuguese import HELP

@Gooey(advanced=True,
       language=LANG,
       navigation='TABBED',
       image_dir=abspath(dirname(realpath(argv[0]))+'/.icons'),
       program_name='labic-ford '+__version__,
       program_description=HELP[0],
       default_size=(640, 670),
       required_cols=2,
       optional_cols=2)

def gooey_parser():
    '''
    Display window with arguments to choose.
    '''
    parser = GooeyParser(add_help=False)
    # add subparser command
    subs = parser.add_subparsers(help='commands', dest='command')
    # load choices lists
    choices_main = list_from_list(ARGS['main'], n=1)
    choices_twitter = list_from_list(ARGS['twitter'], n=1)
    choices_twitter_data = list_from_list(ARGS['twitter_data'], n=1)
    choices_facebook_data = list_from_list(ARGS['facebook_data'], n=1)
    choices_facebook_format = list_from_list(ARGS['facebook_format'], n=1)
    choices_parse = list_from_list(ARGS['parse'], n=1)
    choices_images = list_from_list(ARGS['images'], n=1)
    choices_tools = list_from_list(ARGS['tools'], n=1)
    choices_config = list_from_list(ARGS['configure'], n=1)
    choices_time_format = list_from_list(ARGS['time_format'], n=1)
    choices_quote_format = list_from_list(ARGS['quote_format'], n=1)
    # load unique default values
    current_date = datetime_to_str(datetime_from_timestamp(time()), '%Y/%m/%d')
    current_path = abspath('.')
    # Twitter mining and parsing
    twitter_parser = subs.add_parser(choices_main[0])
    twitter_parser.add_argument('twitter', action='store', choices=choices_twitter, default=choices_twitter[0], help=HELP[1])
    twitter_parser.add_argument('twitter_data', action='store', choices=choices_twitter_data, default=choices_twitter_data[0], help=HELP[2])
    twitter_parser.add_argument('input', action='store', widget='FileChooser', help=HELP[3])
    twitter_parser.add_argument('-d', '--days', action='store', dest='max_days', help=HELP[4])
    twitter_parser.add_argument('-n', '--number', action='store', dest='max_number', help=HELP[5])
    twitter_parser.add_argument('-min', '--minimum', action='store', help=HELP[6])
    twitter_parser.add_argument('-max', '--maximum', action='store', help=HELP[7])
    twitter_parser.add_argument('-l', '--language', action='store', help=HELP[8])
    twitter_parser.add_argument('-g', '--geocodes', action='store', help=HELP[9])
    twitter_parser.add_argument('-p', '--port', action='store', default='8181', help=HELP[10])
    twitter_parser.add_argument('--max-memory', action='store', default=1024, dest='max_memory', help=HELP[12])
    twitter_parser.add_argument('--user-ids', action='store_true', dest='twitter_user_id', help=HELP[13])
    twitter_parser.add_argument('--add-replies', action='store_true', dest='twitter_mine_and_scrap', help=HELP[14])
    twitter_parser.add_argument('--add-images', action='store_true', dest='twitter_mine_images', help=HELP[15])
    twitter_parser.add_argument('--add-parse', action='store_true', default=True, dest='twitter_mine_and_parse', help=HELP[16])
    twitter_parser.add_argument('--ats-only', action='store_true', default=None, dest='stream_ats', help=HELP[18])
    twitter_parser.add_argument('--no-ats', action='store_false', default=None, dest='stream_ats', help=HELP[19])
    twitter_parser.add_argument('--rts-only', action='store_true', default=None, dest='stream_rts', help=HELP[20])
    twitter_parser.add_argument('--no-rts', action='store_false', default=None, dest='stream_rts', help=HELP[21])
    twitter_parser.add_argument('--gephi', action='store_true', default=True, help=HELP[17])
    # Twitter (ExportComments) mining and parsing
    twitter_ec_parse = subs.add_parser(choices_main[0]+' (ExportComments)')
    twitter_ec_parse.add_argument('twitter', action='store', choices=choices_twitter, default=choices_twitter[0], help=HELP[1])
    # Facebook mining and parsing
    facebook_parser = subs.add_parser(choices_main[1])
    facebook_parser.add_argument('facebook_data', action='store', choices=choices_facebook_data, default=choices_facebook_data[0], help=HELP[23])
    facebook_parser.add_argument('facebook_format', action='store', choices=choices_facebook_format, default=choices_facebook_format[0], help=HELP[22])
    facebook_parser.add_argument('input', action='store', widget='FileChooser', help=HELP[24])
    facebook_parser.add_argument('-min', '--minimum', action='store', default=current_date, widget='DateChooser', help=HELP[25])
    facebook_parser.add_argument('-max', '--maximum', action='store', default=current_date, widget='DateChooser', help=HELP[26])
    facebook_parser.add_argument('--max-memory', action='store', default=1024, dest='max_memory', help=HELP[28])
    # images mining
    images_parser = subs.add_parser(choices_main[2])
    images_parser.add_argument('images', action='store', choices=choices_images, default=choices_images[0], help=HELP[30])
    images_parser.add_argument('input_folder', action='store', default=current_path, widget='DirChooser', help=HELP[31])
    images_parser.add_argument('input', action='store', default='(arquivo.csv)' if LANG == 'portuguese' else '(filename.csv)', widget='FileChooser', help=HELP[32])
    images_parser.add_argument('--input-aisi', action='store', widget='FileChooser', help=HELP[33])
    images_parser.add_argument('--input-imgj', action='store', widget='FileChooser', help=HELP[34])
    images_parser.add_argument('--column-usernames', action='store', default='from_user', help=HELP[35])
    images_parser.add_argument('--column-urls', action='store', default='media_url', help=HELP[36])
    # data parse from Facebook and Twitter
    parse_parser = subs.add_parser(choices_main[3])
    parse_parser.add_argument('parse', action='store', choices=choices_parse, default=choices_parse[0], help=HELP[38])
    parse_parser.add_argument('columns', action='store', default='(all columns)', help=HELP[39])
    parse_parser.add_argument('input', action='store', widget='FileChooser', help=HELP[40])
    parse_parser.add_argument('-s', '--strings', action='store', default=[], dest='text_strings', widget='FileChooser', help=HELP[41])
    parse_parser.add_argument('-e', '--exclude', action='store', default=[], dest='exclude_words', widget='FileChooser', help=HELP[42])
    parse_parser.add_argument('-min', '--minimum', action='store', widget='DateChooser', help=HELP[43])
    parse_parser.add_argument('-max', '--maximum', action='store', widget='DateChooser', help=HELP[44])
    parse_parser.add_argument('--concur', action='store', default=2, dest='concur_words', help=HELP[54])
    parse_parser.add_argument('--levels', '--depth', action='store', default=5, dest='depth_words', help=HELP[55])
    parse_parser.add_argument('--time', action='store', choices=choices_time_format, default=choices_time_format[0], dest='time_format', help=HELP[46])
    parse_parser.add_argument('--quote', action='store', choices=choices_quote_format, default=choices_quote_format[0], dest='quote_format', help=HELP[47])
    parse_parser.add_argument('--time-zone', action='store', default=str(int(get_local_tz()/60/60)), help=HELP[48])
    parse_parser.add_argument('-cs', '--case-sensitive', action='store_true', dest='case_sensitive', help=HELP[49])
    parse_parser.add_argument('-W', '--word-wrap', '--wordwrap', action='store_true', help=HELP[50])
    parse_parser.add_argument('-r', '--reverse', action='store_true', help=HELP[51])
    # file tools and operations
    file_parser = subs.add_parser(choices_main[4])
    file_parser.add_argument('tools', action='store', choices=choices_tools, default=choices_tools[0], help=HELP[56])
    file_parser.add_argument('columns', action='store', default='(all columns)', help=HELP[57])
    file_parser.add_argument('input', action='store', default='(arquivo.csv)' if LANG == 'portuguese' else '(filename.csv)', widget='FileChooser', help=HELP[58])
    file_parser.add_argument('input_folder', action='store', default=current_path, widget='DirChooser', help=HELP[59])
    file_parser.add_argument('-s', '--strings', action='store', default=[], dest='text_strings', widget='FileChooser', help=HELP[60])
    file_parser.add_argument('-e', '--exclude', action='store', default=[], dest='exclude_words', widget='FileChooser', help=HELP[61])
    file_parser.add_argument('-min', '--minimum', action='store', widget='DateChooser', help=HELP[62])
    file_parser.add_argument('-max', '--maximum', action='store', widget='DateChooser', help=HELP[63])
    file_parser.add_argument('-n', '--number', action='store', dest='max_number', help=HELP[64])
    file_parser.add_argument('--encode', action='store', choices=['utf8', 'windows-1252', 'ascii'], default='utf8', help=HELP[65])
    file_parser.add_argument('-a', '--all-folders', '--allfolders', action='store_true', dest='merge_subfolders', help=HELP[66])
    file_parser.add_argument('-cs', '--case-sensitive', action='store_true', dest='case_sensitive', help=HELP[67])
    file_parser.add_argument('-W', '--word-wrap', '--wordwrap', action='store_true', help=HELP[68])
    file_parser.add_argument('-r', '--reverse', action='store_true', help=HELP[69])
    # configuration and settings
    cfg_parser = subs.add_parser(choices_main[5])
    cfg_parser.add_argument('configure', action='store', choices=choices_config, default=choices_config[0], help=HELP[70])
    cfg_parser.add_argument('--editor', action='store', help=HELP[71])
    # replace key with value
    return vars(parser.parse_args())