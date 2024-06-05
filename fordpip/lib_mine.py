#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Capture content by connecting to the Facebook/Twitter API or web scraping.

It is required to set credentials beforehand, by running "--configure"
argument on execution or manually editing the script file "config.py".

FACEBOOK: search for pages matching name; mine posts from a list of pages,
groups, events and user profiles using the API (requires key/secret/token);
or scrap posts containing a hashtag (requires usermail/password).

IMAGES: download images from either direct or embedded URLs in a dataset file.

TWITTER: collect past tweets, capture streaming tweets, web scrap for replies
or older tweets via web search engine and list trending topics in a region.
Streaming tweets can be exported to Gephi with the Graph Streaming plugin.
'''

import sys

from os import chdir, environ
from os.path import abspath, basename, isfile
from shutil import move

from .file_merge import file_merge
from .lib_parse import tweets
from .lib_sys import Logger, mkpath

from .facebook_feeds import facebook_feeds
from .hash_collector import scrap_facebook, scrap_tweets # scrap_replies
from .image_crawler import image_crawler
from .image_crawler_v2 import image_crawler_v2
from .cluster_clip import cluster_clip_src
from .pygephi_graphstream import pygephi_graphstream
from .twitter_collect import flashback
from .twitter_network import twitter_network
from .twitter_replies import twitter_replies
from .twitter_trending import trending_topics

TWITTER_KEY = [x.split(",") for x in environ.get("TWITTER_KEY", "").split(";")]
TWITTER_STREAM_KEY = [x.split(",") for x in environ.get("TWITTER_STREAM_KEY", "").split(";")][0]

# twitter functions #

def collect(args):
    '''
    Call flashback script to collect tweets.
    Requires python3-twython and API key/secret.
    '''
    if not TWITTER_KEY[0][0]:
        print("Error: failed to import 'TWITTER_KEY' from the environment.")
        return
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper function or script
    twitter_network(query=args['input'],
        api_keys=TWITTER_KEY,
        query_type=args['twitter_data'],
        query_is_user_id=args['twitter_user_id'],
        max_tweets=int(args['max_number'])\
            if args['max_number']\
            else None)\
    if args['twitter_data'] in ('retweets', 'retweeters', 'friends', 'followers') else\
    flashback(query=args['input'],
        api_keys=TWITTER_KEY,
        query_type=args['twitter_data'],
        query_is_user_id=args['twitter_user_id'],
        coordinates=args['geocodes'],
        lang=args['language'],
        max_days=int(args['max_days'])\
            if args['max_days']\
            else None,
        max_tweets=int(args['max_number'])\
            if args['max_number']\
            else None,
        max_id=int(args['maximum'])\
            if args['maximum']\
            else None,
        since_id=int(args['minimum'])\
            if args['minimum']\
            else None,
        separator=',')
    # execute after-mining actions
    if args['twitter_data'] in ('tweets', 'timeline', 'ids', 'retweets')\
    and any(i in args for i in ['twitter_mine_and_scrap', 'twitter_mine_and_parse', 'twitter_mine_images']):
        # set absolute output file path
        dataset = 'tweets_and_retweets.csv' if args['twitter_data'] == 'retweets' else 'tweets.csv'
        args['input'] = abspath(dataset)
        # scrap @-messages for tweets
        if args['twitter_mine_and_scrap'] and isfile(args['input']):
            args['output'] = 'REPLIES'; print()
            replies(args); chdir('..')
            # update input file to match final dataset
            dataset = 'REPLIES/tweets_and_replies.csv'
            if isfile(dataset): # move to root folder
                move(dataset, 'tweets_and_replies.csv')
                args['input'] = abspath('tweets_and_replies.csv')
         # parse all obtained tweets
        if args['twitter_mine_and_parse'] and isfile(args['input']):
            args['output'] = 'RESULTS'; print()
            tweets(args); chdir('..')
        # get images from dataset
        if args['twitter_mine_images'] and isfile(args['input']):
            args['input'] = basename(args['input']); print()
            image_crawler_v2(args); chdir('..')

# aliases
tweets = timelines = tweet = tweet = retweeters = retweets = user = users = friends = followers = collect

def stream(args):
    '''
    Call pygephi_graphstreaming script to stream tweets.
    Requires python2-tweepy and API key/secret and token/secret.
    '''
    if not TWITTER_KEY[0][0]:
        print("Error: failed to import 'TWITTER_KEY' from the environment.")
        return
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # set external script to call
    script = abspath(args['path_script'] + '/lib/pygephi_graphstreaming/stream.py')
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper function
    pygephi_graphstream(query=args['input'],
        api_key=TWITTER_STREAM_KEY[0],
        api_secret=TWITTER_STREAM_KEY[1],
        token_key=TWITTER_STREAM_KEY[2],
        token_secret=TWITTER_STREAM_KEY[3],
        gephi=args['gephi'],
        max_tweets=int(args['max_number'])\
            if args['max_number']\
            else None,
        port=int(args['port'])\
            if args['port']\
            else None,
        verbose=True if not args['quiet'] else False,
        stream_ats=args['stream_ats'],
        stream_rts=args['stream_rts'],
        script=script)

def stream_beta(args):
    '''
    Stream tweets and display text in terminal.
    Requires python3-twython and API key/secret.
    '''
    if not TWITTER_STREAM_KEY[0]:
        print("Error: failed to import 'TWITTER_STREAM_KEY' from the environment.")
        return
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call script function
    stream_tweets(query=args['input'],
        api_key=TWITTER_STREAM_KEY[0],
        api_secret=TWITTER_STREAM_KEY[1],
        token_key=TWITTER_STREAM_KEY[2],
        token_secret=TWITTER_STREAM_KEY[3],)

def trending(args):
    '''
    Show trending topics on Twitter.
    Requires python3-twython and API key/secret.
    '''
    if not TWITTER_KEY[0][0]:
        print("Error: failed to import 'TWITTER_KEY' from the environment.")
        return
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call script function
    trending_topics(query=args['input'],
        api_keys=TWITTER_KEY,
        show_all_topics=args['verbose'])

def scrap(args):
    '''
    Call hash-collector script to scrap Twitter's web search.
    Optionally requires python3-twython and API key/secret for metadata.
    '''
    if not TWITTER_KEY[0][0]:
        print("Error: failed to import 'TWITTER_KEY' from the environment.")
        return
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # set external script to call
    script = abspath(args['path_script'] + '/lib/hash-collector')
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper script
    scrap_tweets(query=args['input'],
        api_keys=TWITTER_KEY,
        number_of_pages=int(args['max_number'])\
            if args['max_number']\
            else None,
        script_path=script,
        mem_limit=args['max_memory'])

def replies(args):
    '''
    Call hash-collector script to scrap Twitter for replies.
    Optionally requires python3-twython and API key/secret for metadata.
    '''
    if not TWITTER_KEY[0][0]:
        print("Error: failed to import 'TWITTER_KEY' from the environment.")
        return
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # start collecting
    twitter_replies(args['input'], TWITTER_KEY)
    '''# set external script to call
    script = abspath(args['path_script'] + '/lib/hash-collector')
    # call wrapper script
    scrap_replies(input_name=args['input'],
        api_keys=TWITTER_KEY,
        split_tweets=True,
        script_path=script,
        mem_limit=args['max_memory'])'''

# facebook functions #

def feeds(args):
    '''
    Call FacebookFeeds script to mine or search pages.
    Requires Java Runtime Environment (JRE) installed.
    '''
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # set external script to call
    script = abspath(args['path_script'] + '/lib/FacebookFeeds')
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper script
    facebook_feeds(query=args['input'],
        min_date=args['minimum'],
        max_date=args['maximum'],
        facebook_data=args['facebook_data'],
        output_format=args['facebook_format'],
        time_zone=int(args['time_zone'])*60\
            if args['time_zone']\
            else int(-180), # UTC -3 (Brasilia)
        script_path=script)
    # execute Facebook after-mining actions
    if args['facebook_data'] in ('feeds', 'individual', 'posts')\
    and any(i in args for i in ['facebook_mine_and_parse', 'facebook_mine_images']):
        # set absolute output file path
        dataset = 'FaceData.csv'
        args['input'] = abspath(dataset)
        # parse all obtained posts
        if args['facebook_mine_and_parse'] and isfile(args['input']):
            args['output'] = 'RESULTS'; print()
            facebook_parse(args); chdir('..')
        # get images from dataset
        if args['facebook_mine_images'] and isfile(args['input']):
            args['input'] = basename(args['input']); print()
            image_crawler(args); chdir('..')

""" def hashtags(args):
    '''
    Call hash-collector script to scrap hashtag.
    Requires casperjs installed on system.
    '''
    # make new folder and change directory
    mkpath(args['output'] if args['output'] else args['output_path'],
           cd=True, append_date=False if args['output'] else True)
    # set external script to call
    script = abspath(args['path_script'] + '/lib/hash-collector')
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper script
    scrap_facebook(query=args['input'],
        usermail=FACEBOOK_LOGIN[0],
        password=FACEBOOK_LOGIN[1],
        mem_limit=args['max_memory'],
        script_path=script) """

# images functions #

def crawler(args):
    '''
    Call WebCrawler script to get images.
    Requires Java Runtime Environment (JRE) installed.
    '''
    # make new folder and change directory
    # mkpath(args['output'] if args['output'] else args['output_path'],
           # cd=True, append_date=False if args['output'] else True)
    # set external script to call
    script = abspath(args['path_script'] + '/lib/BasicCrawler')
    # start output logger
    if args['log']:
        sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    # call wrapper script
    image_crawler(input_name=basename(args['input']),
        script_path=script,
        column_users=args['column_users'],
        column_urls=args['column_urls'])
        
def crawler_v2(args):
    '''
    Call WebCrawler script to get images.
    Requires Java Runtime Environment (JRE) installed.
    '''
    script = args['path_script']
    
    # start output logger
    #if args['log']:
    #    sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    
    # call wrapper script
    image_crawler_v2(input_name=basename(args['input']),
        script_path=script,
        column_users=args['column_users'],
        column_urls=args['column_urls'])

def cluster_clip(args):
    '''
    Call WebCrawler script to get images.
    Requires Java Runtime Environment (JRE) installed.
    '''
    script = args['path_script']
    # start output logger
    #if args['log']:
    #    sys.stdout = sys.stderr = sys.stdin = Logger(args['log'], 'w')
    
    # call wrapper script
    cluster_clip_src(input_name=basename(args['input']),script_path=script)

