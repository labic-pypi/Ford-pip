#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for analyzing datasets
from flashback and YourTwapperKeeper (legacy) scripts.

The script also accepts exported Gephi network CSV files.
'''

from collections import defaultdict
from csv import reader, QUOTE_MINIMAL
from re import findall
import sys, os
from .lib_gender import *
from .lib_geo import *
from .lib_headers import TWEETS_HEADER, TWEETS_EC_HEADER, TWITTER_USERS_HEADER, YTK_HEADER
from .lib_input import *
from .lib_output import *
from .lib_text import *
from .lib_time import *

try:
    from ftlangdetect import detect
except:
    print('Warning: failed to import ftlangdetect. All content will be considered in pt.')
    def detect(text): return {'lang':'pt'}

def parse_tweets_ec(input_name, quoting=QUOTE_MINIMAL, consider=None,
    time_string='%d/%m/%Y', time_zone=None, geonames=None):
    """
     Analyze output tweets. It is assumed the format is the same of twitter API output.

    Parameters
    ----------
    input_name : str
        The name of .csv/.xlsx file with tweets content.
    quoting : const
        Type of writer uses quote.
    consider : str
	    Name of column. If line contains consider string then this column enters in the parsing process. Else no considers this line.
    time_string: str
	    Specify the format of data. Example: '%d/%m/%Y'.
    time_zone: str
	    Specify the time zone of preference.
    geonames: str
	    Deprecated.

    Returns
    -------
    files : In the same directory returns tops_*.csv, user.csv and location.csv files.

    Raises
    ------
    ReadError
        If file specified in argument input_name don't exist.

    Examples
    --------
    >>> fordpip.parse_tweets('tweets.csv')
    True

    """
    def add_interaction(str_target, str_type):
        # count sent interactions
        dicts_int_sending[str_type][user_name] += 1
        dicts_set_sending[str_type][user_name].add(str_target)
        dicts_set_sending['all'][user_name].add(str_target)
        # count received interactions
        dicts_int_receiving[str_type][str_target] += 1
        dicts_set_receiving[str_type][str_target].add(user_name)
        dicts_set_receiving['all'][str_target].add(user_name)
        # add interacton to network (AT/MT/QT/RT)
        letter = str_type[:1].upper() if str_type != 'reply' else 'A'
        add_to_network(dict_networks[letter+'Ts'],
           [user_name, str_target, str_type, data['tweet_id_(click_to_view_url)'], data['tweet_text'],
           data['favorites'], data['retweets'], data['time']])

    # set default required vars
    delimiter = get_file_delimiter(input_name)
    columns = get_file_header(input_name, title=True)
    columns[0] = 'lineid'
    columns = {x.lower().replace('.','_').replace(' ','_'): i for i,x in enumerate(columns)}
    tz = set_time_zone(time_zone)
    geonames = load_geonames(geonames)
    YourTwapperKeeper = False
    gephi = False

    # check if dataset matches ExportComments fomat
    if set(TWEETS_EC_HEADER).issubset(set(columns.keys())):
        print('Up-to-date tweets dataset found.')
    else:
        print('Warning: dataset does not match ExportComments format.')
        print('Expected:', TWEETS_EC_HEADER)
        print('Received:', list(columns.keys()))
        exit()

    # empty time vars
    min_id = None
    max_id = None
    min_timestamp = None
    max_timestamp= None

    # zero int counters
    int_corrupted_lines = 0
    int_duplicate_lines = 0
    int_ads_lines = 0
    int_different_lang = 0
    int_global_dialogue = 0
    int_global_favorites= 0
    int_global_retweets = 0
    int_global_sentiment = 0
    int_global_users_dialogue = 0

    # empty lists
    # dates = []
    hashtags_by_period = []
    locations = []
    top_dates = []
    top_replies = []
    top_tweets = []
    top_urls = []
    top_users = []
    top_words = []
    top_words_capitalized = []
    users = []
    users_nodes = []
    words_by_period = []

    # empty sets
    set_dates = set()
    set_tids = set()
    set_tweet_ids = set()
    set_users_all = set()
    set_users_tweeting = set()

    # empty dictionaries
    dict_hashtags = {}
    dict_tweets = {}

    # empty list dictionaries
    top_tweets_by_date = defaultdict(list)
    dict_networks = defaultdict(list)
    dict_capitalized_dates = defaultdict(list)
    dict_emojis_dates = defaultdict(list)
    dict_hashtags_dates = defaultdict(list)
    dict_words_dates = defaultdict(list)
    # dict_lines = defaultdict(list)

    # empty int dictionaries
    dict_int_capitalized = defaultdict(int)
    dict_int_countries = defaultdict(int)
    dict_int_emojis = defaultdict(int)
    dict_int_favorites = defaultdict(int)
    dict_int_hashtags = defaultdict(int)
    dict_int_influence = defaultdict(int)
    dict_int_lang = defaultdict(int)
    dict_int_media = defaultdict(int)
    dict_int_original_tweets = defaultdict(int)
    dict_int_places = defaultdict(int)
    dict_int_quotes = defaultdict(int)
    dict_int_replies = defaultdict(int)
    dict_int_retweets = defaultdict(int)
    dict_int_sentiment = defaultdict(int)
    dict_int_source = defaultdict(int)
    dict_int_text = defaultdict(int)
    dict_int_total = defaultdict(int)
    dict_int_tweets = defaultdict(int)
    dict_int_type = defaultdict(int)
    dict_int_urls = defaultdict(int)
    dict_int_user_favorites = defaultdict(int)
    dict_int_user_retweets = defaultdict(int)
    dict_int_user_tweets = defaultdict(int)
    dict_int_words = defaultdict(int)
    dict_int_words_favorited = defaultdict(int)
    dict_int_words_retweeted = defaultdict(int)
    dict_int_words_favorited_capitalized = defaultdict(int)
    dict_int_words_retweeted_capitalized = defaultdict(int)

    # empty set dictionaries
    dict_set_hashtags = defaultdict(set)
    dict_set_media = defaultdict(set)
    dict_set_urls = defaultdict(set)
    dict_set_tweets_date = defaultdict(set)

    # occurrences by period
    dicts_int_hashtags_by_date = defaultdict(lambda:defaultdict(int))
    dicts_int_words_by_date = defaultdict(lambda:defaultdict(int))

    # tweet, hashtag, sentiment, retweet, reply, quote, mention
    dicts_int_dates = defaultdict(lambda:defaultdict(int))

    # retweet, reply, quote, mention
    dicts_int_receiving = defaultdict(lambda:defaultdict(int))
    dicts_int_sending = defaultdict(lambda:defaultdict(int))

    # retweet, reply, quote, mention, all
    dicts_set_receiving = defaultdict(lambda:defaultdict(set))
    dicts_set_sending = defaultdict(lambda:defaultdict(set))

    idiomas_possiveis = ['pt', 'en', 'es', 'fr', 'it']
    while True:
        print('Deseja filtrar os tweets por algum idioma? [pt, en, es, fr, it]')
        print('Caso não queira filtrar, deixe em branco.')
        print('Digite os idiomas separados por vírgula: ', end='')
        idiomas = input().split(',')
        idiomas = [idioma.strip().lower() for idioma in idiomas]
        if idiomas == ['']:
            idiomas = None
            break
        else:
            idiomas_incorretos = [idioma for idioma in idiomas if idioma not in idiomas_possiveis]
            idiomas = [idioma for idioma in idiomas if idioma in idiomas_possiveis]
            if idiomas_incorretos:
                print('Idiomas inválidos:', idiomas_incorretos)
                continue
            break

    header = None
    print('Parsing tweets...')

    # start file reading
    with open(input_name, 'rt', encoding='utf8') as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting)
        header = next(file_reader) # skips the first line

        if len(header) == 20:
            header = header + ['Profile URL']

        with open('users.csv', 'wt', encoding='utf8') as users_file:
            users_writer = writer(users_file, delimiter=delimiter, quoting=quoting)
            users_writer.writerow(TWITTER_USERS_HEADER)

            # iterate through lines
            for line in file_reader:
                time_to_print(file_reader.line_num)
                geo_name = False
                has_emoji = False
                target = None
                sent_value = 0
                # word_pos = 0
                hashtags = []
                mentions_user = []
                urls = []
                words_read = set()
                words_capitalized_read = set()

                if len(line) == 20: line = line + ['']
                if len(line) == 22 and line[21].startswith('https://'): line = line[:-1]

                # avoid uneven length lines
                if len(line) != len(header):
                    print(header)
                    print(line)
                    print('Warning: line', str(file_reader.line_num) + ',', 'list index got', len(line), 'and expected', len(header), 'columns.')
                    int_corrupted_lines += 1
                    continue # skip

                elif line == header:
                    print('Warning: line', str(file_reader.line_num) + ',', 'duplicate header.')
                    continue # skip

                try: # analyze
                    data = read_line(line, columns)
                    
                    # Ads: Twitter for Advertisers, advertiser-interface, Sprinklr Publishing, Twitter Ads, simpleads-ui, Sprinklr, CTW AMS.
                    if data['tweet_source'] in ['advertiser-interface','Twitter for Advertisers','Twitter Ads','simpleads-ui','Sprinklr','Sprinklr Publishing','CTW AMS']:
                        int_ads_lines += 1
                        continue # skip

                    # define tweet lang
                    # data['lang'] = 'pt'
                    try:
                        data['lang'] = detect(data['tweet_text'])['lang']
                    except:
                        data['lang'] = 'pt'

                    # filter by language
                    if idiomas and data['lang'] not in idiomas:
                        int_different_lang += 1
                        continue

                    # remove start of id
                    data['tweet_id_(click_to_view_url)'] = data['tweet_id_(click_to_view_url)'].replace('ID: ','')

                    # avoid duplicates
                    if data['tweet_id_(click_to_view_url)'] in set_tweet_ids:
                        int_duplicate_lines += 1
                        continue # skip
                    set_tweet_ids.add(data['tweet_id_(click_to_view_url)'])

                    # parse only tweets containing value
                    if consider and consider in data:
                        if data[consider] == '':
                            continue # skip

                    # get ID range
                    if not min_id or int(data['tweet_id_(click_to_view_url)']) < min_id:
                        min_id = int(data['tweet_id_(click_to_view_url)'])
                    if not max_id or int(data['tweet_id_(click_to_view_url)']) > max_id:
                        max_id = int(data['tweet_id_(click_to_view_url)'])

                    # timestamp fix
                    if 'date' in columns:
                        # Convert datetime string to timestamp
                        try:
                            data['time'] = str(int(datetime_from_str(data['date'], str_format='%Y-%m-%d %H:%M:%S').timestamp()))
                        except:
                            try:
                                data['time'] = str(int(datetime_from_str(data['date'], str_format='%Y-%m-%d %H:%M:%S.%f').timestamp()))
                            except:
                                try:
                                    data['time'] = str(int(datetime_from_str(data['date'], str_format='%d/%m/%y %H:%M:%S').timestamp()))
                                except:
                                    data['time'] = str(int(datetime_from_str(data['date'], str_format='%d/%m/%Y %H:%M:%S').timestamp()))

                    # get timestamp range
                    if not min_timestamp or int(data['time']) < min_timestamp:
                        min_timestamp = int(data['time'])
                    if not max_timestamp or int(data['time']) > max_timestamp:
                        max_timestamp = int(data['time'])

                    # get date
                    date = datetime_from_timestamp(int(data['time']), tz)
                    str_date = datetime_to_str(date, time_string)
                    set_dates.add(str_date)
                    str_date_short = datetime_to_str(date, '%Y-%m-%d')
                    if str_date_short not in top_tweets_by_date: top_tweets_by_date[str_date_short] = []
                    top_tweets_by_date[str_date_short].append(data)
                    # dates.append(date)

                    # clean line breaks from text
                    for text in ['text', 'rt_text', 'quoted_text', 'tweet_text', 'author_bio', 'author_location']:
                        if text in data: # check for field data first
                            data[text] = data[text].replace('\n', ' ').replace('\r', ' ')

                    # count retweets
                    if data['tweet_text'].endswith('…') and data['tweet_text'].startswith('RT @'):
                      try: # expand from retweeted text
                        a,b = data['tweet_text'].rstrip('…').split(': ',1)
                        data['rt_user'] = a.replace('RT @','')
                        data['tweet_text'] = b
                        data['type'] = 'retweet'
                      except: pass

                    # count replies
                    if data['tweet_text'].startswith('@'):
                        data['type'] = 'reply'
                        data['reply_to_user'] = data['tweet_text'].split()[0].replace('@','')

                    # text and sentiment
                    for word in data['tweet_text'].split():

                        # word_pos += 1

                        if is_emoji(word):
                            has_emoji = True
                            sent_value += get_emoji_value(word)
                            add_to_dicts(word, dict_int_emojis, dict_emojis_dates, date)

                        elif is_hashtag(word):
                            hashtags.append(word)

                        elif is_mention(word):
                            mentions_user.append(word[1:]) # remove @

                        elif is_url(word):
                            urls.append(word)

                        else: # common word
                            str_word = clear_word(word)
                            if check_word(str_word):
                                words_read.add(str_word)
                                if word == word.capitalize():
                                    words_capitalized_read.add(str_word.capitalize())

                    data['hashtags'] = str_from_list(hashtags)
                    data['mentions_user'] = str_from_list(mentions_user)
                    data['urls'] = str_from_list(urls)

                    if has_emoji:
                        dicts_int_dates['sentiment'][str_date] += sent_value
                        dict_int_sentiment[data['tweet_text']] = sent_value
                        dict_int_total['emoji'] += 1
                        int_global_sentiment += sent_value

                    if not data['comments']: data['comments'] = 0
                    if data['comments'] == '': data['comments'] = 0


                    for word in words_read:
                        add_to_dicts(word, dict_int_words, dict_words_dates, date)
                        if not data['favorites']: data['favorites'] = 0
                        dict_int_words_favorited[word] += int(data['favorites'])
                        dicts_int_words_by_date[str_date][word] += 1

                    for word in words_capitalized_read:
                        add_to_dicts(word.capitalize(), dict_int_capitalized, dict_capitalized_dates, date)
                        dict_int_words_favorited_capitalized[word] += int(data['favorites'])

                    # get user_name
                    user_name = data['username'].lower()
                    set_users_all.add(user_name)

                    # get tweet URL
                    tweet_url = data['status_url']

                    # define tweet type
                    if 'type' not in data: data['type'] = 'tweet'
                    if data['is_retweet?'] == 'yes': data['type'] = 'retweet'

                    # add retweet metadata to dictionary
                    tid = data['tweet_id_(click_to_view_url)']

                    if not data['favorites']: data['favorites'] = 0
                    if not data['retweets']: data['retweets'] = 0
                    if not data['author_followers']: data['author_followers'] = 0
                    if not data['author_friends']: data['author_friends'] = 0

                    engagement = int(data['favorites']) + int(data['retweets'])
                    data['engagement'] = engagement
                    ttext = data['tweet_text']
                    user_posting = user_name

                    if engagement > 0 and (tid not in set_tids):
                        set_tids.add(tid) # avoid duplicates
                        dict_int_tweets[tid] = engagement
                        dict_tweets[tid] = {'text': ttext,
                                            'from_user': user_posting,
                                            'hashtags': str_from_list(hashtags),
                                            'rt_count': data['retweets'],
                                            'favorite_count': data['favorites'],
                                            'type': data['type'],
                                            'lang': data['lang'],
                                            'place': data['author_location'],
                                            'country': None,
                                            'source': data['tweet_source'],
                                            'media':None,
                                            'created_at': data['date'],
                                            'url': data['status_url'] }

                    # add user metadata to set
                    if user_name not in set_users_tweeting:
                        users_writer.writerow([data.get(i) for i in TWITTER_USERS_HEADER])
                        if not gephi:
                            users_nodes.append([user_name, int(data['author_followers']), int(data['author_friends']), data['engagement']])
                        set_users_tweeting.add(user_name)

                    # calculate statistics
                    dicts_int_dates[data['type']][str_date] += 1
                    dict_int_text[ttext] += 1
                    dict_int_lang[data['lang']] += 1
                    dict_int_source[data['tweet_source']] += 1
                    dict_int_type[data['type']] += 1
                    dict_int_user_tweets[user_name] += 1
                    dict_set_tweets_date[str_date].add(user_name)

                    # original tweets
                    if data['type'] == 'tweet':
                        # count original tweets
                        dict_int_original_tweets[user_name] += 1
                        # count word retweeted times
                        for word in words_read:
                            dict_int_words_retweeted[word] += int(data['retweets'])
                        for word in words_capitalized_read:
                            dict_int_words_retweeted_capitalized[word] += int(data['retweets'])

                    # count retweets and replies
                    if data['type'] in ('retweet', 'reply', 'quote', 'reply'):
                        target = data['rt_user'] if data['type'] == 'retweet' else data['reply_to_user']
                        target = data['quoted_user'] if data['type'] == 'quote' else target
                        add_interaction(target.lower(), data['type'])
                        set_users_all.add(target.lower())

                    # get retweeted value from Twitter
                    if data['retweets'] and int(data['retweets']) > 0:
                        int_global_retweets += int(data['retweets']) if data['type'] != 'retweet' else 0
                        dict_int_user_retweets[user_name] += int(data['retweets']) if data['type'] != 'retweet' else 0
                        dict_int_retweets[data['tweet_text']] = int(data['retweets'])

                    # get likes/favorites value from Twitter
                    if data['favorites'] and int(data['favorites']) > 0:
                        int_global_favorites += int(data['favorites'])
                        dict_int_user_favorites[user_name] += int(data['favorites'])
                        dict_int_favorites[data['tweet_text']] += int(data['favorites'])

                    # count mentions
                    if 'mentions_user' in data and data['mentions_user']:
                        dict_int_total['mention'] += 1
                        mentions_list = str_to_list(data['mentions_user'])

                        for mention in mentions_list:
                            mention = remove_punctuation_special(mention).lower()

                            if mention != target:
                                dicts_int_dates['mention'][str_date] += 1
                                add_interaction(mention, 'mention')
                                set_users_all.add(mention)

                    # count hashtags
                    if 'hashtags' in data and data['hashtags']:
                        dict_int_total['hashtag'] += 1
                        hashtags_list = str_to_list(data['hashtags'])
                        valid_hashtags = []

                        for hashtag in hashtags_list:
                            valid_hashtags.append('#'+clear_word(hashtag.lower()))

                        for hashtag in valid_hashtags:
                            dicts_int_dates['hashtag'][str_date] += 1
                            dicts_int_hashtags_by_date[str_date][hashtag] += 1
                            add_to_dicts(hashtag, dict_int_hashtags, dict_hashtags_dates, date, dict_set_hashtags, user_name)
                            add_to_network(dict_networks['hashtags_users'], [user_name, hashtag])

                        for combination in list_combinations(valid_hashtags):
                            add_to_network(dict_networks['hashtags'], [combination[0], combination[1]])

                    # count URLs
                    if 'urls' in data and data['urls']:
                        dict_int_total['url'] += 1
                        urls_list = str_to_list(data['urls'], separator=', ')\
                            if isinstance(data['urls'], str) else data['urls']
                        for url in urls_list:
                            try: # each
                                url_domain = findall(r'(?<=://)[a-zA-Z0-9_.]+', url)[0].replace('www.','')
                                add_to_dicts(url, dict_int_urls, dict_set=dict_set_urls, item=user_name)
                                add_to_network(dict_networks['URLs_full'], [user_name, url])
                                add_to_network(dict_networks['URLs'], [user_name, url_domain])
                                if any(u in url for u in ['facebook.com', 'fb.me']):
                                    add_to_network(dict_networks['URLs_facebook'], [user_name, url])
                                if any (u in url for u in ['youtube.com', 'youtu.be']):
                                    add_to_network(dict_networks['URLs_youtube'], [user_name, url])
                            except: pass

                    # get most quoted ID
                    if data['type'] == 'quote':
                        dict_int_quotes[data['quoted_text']] += 1

                    # get most replied ID
                    # if data['type'] == 'reply':
                    #    dict_int_replies[data['reply_to_id']] += 1

                    # count embedded media
                    if 'media_url' in data and data['media_url']:
                        dict_int_total['media_url'] += 1
                        add_to_dicts(data['media_url'], dict_int_media, dict_set=dict_set_media, item=user_name)

                    # count location
                    if 'place' in data and data['place']:
                        dict_int_total['place'] += 1
                        dict_int_countries[data['country']] += 1
                        dict_int_places[data['place'] + ' (' + data['country'] + ')'] += 1
                        geo_name = data['place'].split(',')[0].replace(',','').replace('-','').lower()
                        ccode = data['country_code'] if 'country_code' in data else None

                    # count geocode locations by Twitter
                    if 'geo_type' in data and data['geo_type'].lower() == 'point':
                        dict_int_total['geocode'] += 1
                        # append coordinates to locations output file
                        locations.append([data['latitude'], data['longitude'], 'point', data['place'],
                                          data['country'], ccode, data['lang'], data['time'], data['from_user'],
                                          data['text'], data['user_image_url'], tweet_url])

                    # try and match reverse geocode by country
                    elif geo_name and ccode in geonames.keys()\
                    and geo_name in geonames[ccode].keys():
                        dict_int_total['in_geonames'] += 1
                        latitude, longitude, geoname, = get_geoname(geo_name, geonames, ccode)
                        # append coordinates to locations output file
                        locations.append([latitude, longitude, geoname, data['place'],
                                          data['country'], ccode, data['lang'], data['time'], data['from_user'],
                                          data['text'], data['user_image_url'], tweet_url])

                except Exception as e:
                    print('Warning: line', str(file_reader.line_num) + ',', str(e) + '.')
                    # Printa a linha do script que deu erro
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    print(exc_type, fname, exc_tb.tb_lineno)
                    int_corrupted_lines += 1

    int_total_lines = file_reader.line_num
    int_valid_lines = int_total_lines - int_corrupted_lines - int_duplicate_lines - 1
    int_valid_lines = int_valid_lines - int_ads_lines - int_different_lang

    for k,v in top_tweets_by_date.items():
        # Sort tweets by retweets
        top_tweets_by_date[k] = sorted(v, key=lambda x: int(x['retweets']), reverse=True)
        # Remove tweets with no replies
        top_tweets_by_date[k] = [x for x in top_tweets_by_date[k] if int(x['comments']) > 0]
        # Keep only top 10 tweets
        top_tweets_by_date[k] = top_tweets_by_date[k][:10]

    # Add total user retweets to user_nodes
    for user in users_nodes:
        user.append(dict_int_user_retweets[user[0]])

    print('Read', int_total_lines, 'total lines.')
    print(int_corrupted_lines, 'corrupted lines.') if int_corrupted_lines > 0 else None
    print(int_ads_lines, 'ads lines.') if int_ads_lines > 0 else None
    print(int_different_lang, 'different language lines.') if int_different_lang > 0 else None
    print(int_duplicate_lines, 'duplicate tweets.') if int_duplicate_lines > 0 else None
    print(int_valid_lines, 'valid lines.') if int_valid_lines > 0 else None

    if int_valid_lines == 0:
        print('Error: not enough data to parse.')
        return

    # analyze data
    int_tweets = len(set_tweet_ids)
    int_original = dict_int_type['tweet']
    int_quotes = dict_int_type['quote']
    int_retweets = dict_int_type['retweet']
    int_replies = dict_int_type['reply']
    int_mentions = sum(dicts_int_sending['mention'].values())
    int_interactions = int_retweets + int_replies + int_mentions
    int_country = len(dict_int_countries)
    int_emojis = len(dict_int_emojis)
    int_hashtags = len(dict_int_hashtags)
    int_lang = len(dict_int_lang)
    int_media = len(dict_int_media)
    int_places = len(dict_int_places)
    int_sources = len(dict_int_source)
    int_urls = len(dict_int_urls)
    int_words = len(dict_int_words)
    int_geocoded = dict_int_total['in_geonames']
    int_tweets_with_emoji = dict_int_total['emoji']
    int_tweets_with_geocode = dict_int_total['geocode'] + int_geocoded
    int_tweets_with_hashtag = dict_int_total['hashtag']
    int_tweets_with_media = dict_int_total['media_url']
    int_tweets_with_mention = dict_int_total['mention']
    int_tweets_with_place = dict_int_total['place']
    int_tweets_with_url = dict_int_total['url']
    int_users = len(set_users_all)
    int_users_op = len(dict_int_original_tweets)
    int_users_tweeting = len(dict_int_user_tweets)
    int_users_retweeting = len(dicts_set_sending['retweet'])
    int_users_retweeted = len(dicts_set_receiving['retweet'])
    int_users_quoting = len(dicts_set_sending['quote'])
    int_users_quoted = len(dicts_set_receiving['quote'])
    int_users_replying = len(dicts_set_sending['reply'])
    int_users_replied = len(dicts_set_receiving['reply'])
    int_users_mentioning = len(dicts_set_sending['mention'])
    int_users_mentioned = len(dicts_set_receiving['mention'])
    int_users_senders = len(dicts_set_sending['all'])
    int_users_receivers = len(dicts_set_receiving['all'])
    dicts_int_dates['user'] = dict_of_int_from_dict_of_lists(dict_set_tweets_date)

    # unshorten top URLs
    # print('\nUnshortening top 10 URLs...')
    # for url in get_N_first(dict_int_urls, 10):
    #     times_tweeted = dict_int_urls[url]
    #     unique_users = len(dict_set_urls[url])
    #     try: url = expand_url(url) if is_url_shortened(url) else url
    #     except: print('Warning: unable to expand URL ' + url + '.')
    #     else: top_urls.append([url, times_tweeted, unique_users])

    # get a timeline of hashtags
    for hashtag in get_N_first(dict_int_hashtags, 50):
        line = [hashtag]
        for date in sorted(set_dates):
            line.append(dicts_int_hashtags_by_date[date][hashtag])
        hashtags_by_period.append(line)

    # get a timeline of words
    for word in get_N_first(dict_int_words, 50):
        line = [word]
        for date in sorted(set_dates):
            line.append(dicts_int_words_by_date[date][word])
        words_by_period.append(line)

    # get top dates
    for date in set_dates:
        original = dicts_int_dates['tweet'][date]
        retweets = dicts_int_dates['retweet'][date]
        replies = dicts_int_dates['reply'][date]
        quotes = dicts_int_dates['quote'][date]
        tweets = original + retweets + replies
        usernames = dicts_int_dates['user'][date]
        mentions = dicts_int_dates['mention'][date]
        hashtags = dicts_int_dates['hashtag'][date]
        sentiment = dicts_int_dates['sentiment'][date]
        top_dates.append([date, usernames, tweets, original, retweets, replies, mentions, hashtags, sentiment])

    # get top users
    for user in set_users_all:
        # main tweet metadata
        tweets = dict_int_user_tweets[user] if user in dict_int_user_tweets else 0
        rt_count = dict_int_user_retweets[user] if user in dict_int_user_retweets else 0
        favorite_count = dict_int_user_favorites[user] if user in dict_int_user_favorites else 0
        # unique tweet interactions
        qts_in = dicts_int_receiving['quote'][user] if user in dicts_int_receiving['quote'] else 0
        qts_out = dicts_int_sending['quote'][user] if user in dicts_int_sending['quote'] else 0
        rts_in = dicts_int_receiving['retweet'][user] if user in dicts_int_receiving['retweet'] else 0
        rts_out = dicts_int_sending['retweet'][user] if user in dicts_int_sending['retweet'] else 0
        ats_in = dicts_int_receiving['reply'][user] if user in dicts_int_receiving['reply'] else 0
        ats_out = dicts_int_sending['reply'][user] if user in dicts_int_sending['reply'] else 0
        mts_in = dicts_int_receiving['mention'][user] if user in dicts_int_receiving['mention'] else 0
        mts_out = dicts_int_sending['mention'][user] if user in dicts_int_sending['mention'] else 0
        # unique user interactions
        qts_users_in = len(dicts_set_receiving['quote'][user]) if user in dicts_set_receiving['quote'] else 0
        qts_users_out = len(dicts_set_sending['quote'][user]) if user in dicts_set_sending['quote'] else 0
        rts_users_in = len(dicts_set_receiving['retweet'][user]) if user in dicts_set_receiving['retweet'] else 0
        rts_users_out = len(dicts_set_sending['retweet'][user]) if user in dicts_set_sending['retweet'] else 0
        ats_users_in = len(dicts_set_receiving['reply'][user]) if user in dicts_set_receiving['reply'] else 0
        ats_users_out = len(dicts_set_sending['reply'][user]) if user in dicts_set_sending['reply'] else 0
        mts_users_in = len(dicts_set_receiving['mention'][user]) if user in dicts_set_receiving['mention'] else 0
        mts_users_out = len(dicts_set_sending['mention'][user]) if user in dicts_set_sending['mention'] else 0
        # total user/tweet unique interactions
        total_users_in = len(dicts_set_receiving['all'][user]) if user in dicts_set_receiving['all'] else 0
        total_users_out = len(dicts_set_sending['all'][user]) if user in dicts_set_sending['all'] else 0
        total_users = len(set(list(dicts_set_receiving['all'][user]) + list(dicts_set_sending['all'][user])))
        total_in = (rts_in + ats_in + mts_in)
        total_out = (rts_out + ats_out + mts_out)
        total = (total_in + total_out)
        # influence index (user impact)
        if tweets > 0:
            influence = (rts_in/tweets)
            dict_int_influence['@'+user] = influence
            influence = str_from_num(influence)
        else: influence = None
        # dialogue index (@-message intensity)
        if (ats_in+ats_out) > 0:
            dialogue = (ats_out/(ats_in+ats_out))
            int_global_dialogue += dialogue
            dialogue = str_from_num(dialogue)
            int_global_users_dialogue += 1
        else: dialogue = None
        # plurality index (interaction uniqueness)
        plurality = str_from_num(total_users/total) if total > 0 else None
        # add user activity to set
        top_users.append([user, tweets, rt_count, favorite_count,
                          influence, dialogue, plurality,
                          rts_in, rts_users_in, rts_out, rts_users_out,
                          ats_in, ats_users_in, ats_out, ats_users_out,
                          mts_in, mts_users_in, mts_out, mts_users_out,
                          total_in, total_users_in, total_out, total_users_out,
                          total, total_users])

    # get top retweeted tweets
    for tweet_id in get_N_first(dict_int_tweets, 5000):
        text =  dict_tweets[tweet_id]['text']
        from_user = dict_tweets[tweet_id]['from_user']
        hashtags =  dict_tweets[tweet_id]['hashtags']
        rt_count =  dict_tweets[tweet_id]['rt_count']
        favorite_count =  dict_tweets[tweet_id]['favorite_count']
        txt_count = dict_int_text[text] # <== tweet_text counter
        ttype =  dict_tweets[tweet_id]['type']
        lang =  dict_tweets[tweet_id]['lang']
        place =  dict_tweets[tweet_id]['place']
        country =  dict_tweets[tweet_id]['country']
        source =  dict_tweets[tweet_id]['source']
        media =  dict_tweets[tweet_id]['media']
        url =  dict_tweets[tweet_id]['url']
        date =  dict_tweets[tweet_id]['created_at']
        top_tweets.append([text, from_user, tweet_id, hashtags, rt_count, favorite_count,
                           txt_count, ttype, lang, place, country, source, media, date, url])

    # get top words
    for word in get_N_first(dict_int_words, 250):
        times = dict_int_words[word]
        likes = dict_int_words_favorited[word]
        retweets = dict_int_words_retweeted[word]
        top_words.append([word, times, likes, retweets])

    # get top capitalized words
    for word in get_N_first(dict_int_capitalized, 250):
        times = dict_int_capitalized[word]
        gender = gender_identify(word)
        likes = dict_int_words_favorited_capitalized[word]
        retweets = dict_int_words_retweeted_capitalized[word]
        top_words_capitalized.append([word, times, gender, likes, retweets])

    # write datasets by type
    # for key in dict_lines.keys():
        # write_set(('dataset_' + key + '.csv'), dict_lines[key], header)

    header_edges=['type VARCHAR', 'tweet_id VARCHAR', 'text VARCHAR',
        'favorite_count INT', 'rt_count INT', 'time INT']

    for key in dict_networks.keys():
        write_gdf(
            ('network_' + key + '.gdf'),
            dict_networks[key],
            nodes=users_nodes,
            header_nodes=["user_followers INT", "user_following INT", "user_retweets INT, user_engagement INT"],
            header_edges=header_edges if all(i not in key for i in ['hashtags', 'URLs']) else [],
            directed=True if key != 'hashtags' else False)

    write_set('locations.csv', locations,
        ['latitude', 'longitude', 'geo_type', 'place', 'country', 'country_code', 'lang', 'time', 'user', 'text', 'image_url', 'url'])

    write_set('top_dates.csv', top_dates,
        ['date', 'users', 'tweets', 'original', 'retweets', 'replies', 'mentions', 'hashtags', 'sentiment'])

    write_set('top_tweets.csv', top_tweets,
        ['text', 'from_user', 'tweet_id', 'hashtags', 'rt_count', 'favorite_count', 'tweet_count', 'type', 'lang', 'place', 'country', 'source', 'media', 'date', 'url'])

    # write_set('top_urls_full.csv', top_urls,
        # ['url_full', 'times_tweeted', 'unique_users'])

    write_set('top_users.csv', top_users,
        ['from_user',  'tweets_published', 'retweet_count', 'favorite_count',
         'influence', 'dialogue_%', 'plurality_%',
         'retweets_in', 'retweets_users_in', 'retweets_out', 'retweets_users_out',
         'replies_in', 'replies_users_in', 'replies_out', 'replies_users_out',
         'mentions_in', 'mentions_users_in', 'mentions_out', 'mentions_users_out',
         'total_in', 'total_users_in', 'total_out', 'total_users_out',
         'total', 'total_users'])

    write_set('top_hashtags_by_period.csv', hashtags_by_period,
        ['hashtag']+list(sorted(set_dates)))

    write_set('top_words_by_period.csv', words_by_period,
        ['word']+list(sorted(set_dates)))

    write_set('top_words.csv', top_words,
        ['word', 'times_mentioned', 'likes', 'retweets'])

    write_set('top_words_capitalized.csv', top_words_capitalized,
        ['word', 'times_mentioned', 'name_gender', 'likes', 'retweets'])

    write_values('top_countries.csv', dict_int_countries, ['country', 'tweets', 'tweets_%'], pct=True)
    write_values('top_emojis.UTF16.csv', dict_int_emojis, ['emoji', 'times_tweeted'], encoding='utf16')
    write_values('top_favorites.csv', dict_int_favorites, ['tweet', 'favorite_count'])
    write_values('top_hashtags.csv', dict_int_hashtags, ['hashtag', 'times_mentioned'])
    write_values('top_lang.csv', dict_int_lang, ['lang', 'tweets', 'tweets_%'], pct=True)
    write_values('top_media.csv', dict_int_media, ['media_url', 'times_tweeted'])
    write_values('top_places.csv', dict_int_places, ['place', 'tweets', 'tweets_%'], pct=True)
    write_values('top_quotes.csv', dict_int_quotes, ['tweet', 'times_quoted'])
    write_values('top_replies.csv', dict_int_replies, ['tweet', 'reply_count'])
    write_values('top_retweets.csv', dict_int_retweets, ['tweet', 'rt_count'])
    write_values('top_sentiments.UTF16.csv', dict_int_sentiment, ['tweet', 'sent_value'], encoding='utf16')
    write_values('top_source.csv', dict_int_source, ['source', 'tweets', 'tweets_%'], pct=True)
    write_values('top_text.csv', dict_int_text, ['tweet', 'txt_count'])
    write_values('top_type.csv', dict_int_type, ['type', 'tweets', 'tweets_%'], pct=True)
    write_values('top_URLs.csv', dict_int_urls, ['url', 'times_tweeted'])
    # write_values('top_words.csv', dict_int_words, ['word', 'times_mentioned'])
    # write_values('top_words_liked.csv', dict_int_words_favorited, ['word', 'favorite_count'])
    # write_values('top_words_retweeted.csv', dict_int_words_retweeted, ['word', 'rt_count'])
    # write_values('top_words_capitalized_liked.csv', dict_int_words_favorited_capitalized, ['word', 'favorite_count'])
    # write_values('top_words_capitalized_retweeted.csv', dict_int_words_retweeted_capitalized, ['word', 'rt_count'])

    write_values('top_hashtags_by_users.csv', dict_set_hashtags, ['hashtag', 'unique_users'],
        value_format_function=lambda t: len(t))
    write_values('top_media_by_users.csv', dict_set_media, ['media_url', 'unique_users'],
        value_format_function=lambda t: len(t))
    write_values('top_urls_by_users.csv', dict_set_urls, ['url', 'unique_users'],
        value_format_function=lambda t: len(t))
    
    top_tweets_by_date_set = set()
    for k,v in top_tweets_by_date.items():
        for tweet in v:
            replies_url = f"https://twitter.com/search?q=conversation_id%3A{tweet['tweet_id_(click_to_view_url)']}%20filter%3Areplies&src=typed_query&f=live"
            tpl = (k,) + tuple(tweet.values()) + (replies_url,)
            top_tweets_by_date_set.add(tpl)
    # Sort set by date and retweets
    top_tweets_by_date_set = sorted(top_tweets_by_date_set, key=lambda x: (x[0], int(x[6])), reverse=True)
    write_set('top_tweets_by_date.csv', top_tweets_by_date_set,
              header=['Data'] + header + ['Replies URL'])

    ''' # write_timeline() => WIP (work in progress)
    write_timeline('timeline_words_capitalized.csv', dict_capitalized_dates, get_N_first(dict_int_capitalized, 25), dates)
    write_timeline('timeline_words.csv', dict_words_dates, get_N_first(dict_int_words, 25), dates)
    write_timeline('timeline_hashtags.csv', dict_hashtags_dates, get_N_first(dict_int_hashtags, 25), dates)
    write_timeline('timeline_emojis.csv', dict_emojis_dates, get_N_first(dict_int_emojis, 25), dates) '''

    write_wordcloud('wordcloud_words.txt', dict_int_words)
    write_wordcloud('wordcloud_hashtags.txt', dict_int_hashtags)

    # get time range
    min_date = datetime_from_timestamp(min_timestamp, utc=True)
    max_date = datetime_from_timestamp(max_timestamp, utc=True)
    time_diff, time_string, seconds = get_time_diff(max_date, min_date)

    # get frequency
    frequency_tweet = int_tweets/time_diff if time_diff > 0 else 0
    frequency_favorite = int_global_favorites/time_diff if time_diff > 0 else 0
    frequency_retweet = int_global_retweets/time_diff if time_diff > 0 else 0

    # get global values
    global_dialogue = int_global_dialogue/int_global_users_dialogue if int_global_users_dialogue > 0 else 'None'
    global_sentiment = int_global_sentiment/int_tweets_with_emoji if int_tweets_with_emoji > 0 else 'None'

    # get top stats
    top_country = get_N_first(dict_int_countries, 1)[0] if dict_int_countries else 'None'
    top_favorite = get_N_first(dict_int_favorites, 1) if dict_int_favorites else 'None'
    top_hashtags = get_N_first(dict_int_hashtags, 5) if dict_int_hashtags else 'None'
    top_lang = get_N_first(dict_int_lang, 1)[0] if dict_int_lang else 'None'
    top_source = get_N_first(dict_int_source, 1)[0] if dict_int_source else 'None'
    top_url = get_N_first(dict_int_urls, 1) if dict_int_urls else 'None'
    top_retweet = get_N_first(dict_int_retweets, 1) if dict_int_retweets else 'None'
    top_usernames = get_N_first(dict_int_influence, 5) if dict_int_influence else 'None'
    top_words =  get_N_first(dict_int_words, 5) if dict_int_words else 'None'

    # convert to strings
    min_date = datetime_to_str(min_date, '%a %b %d %H:%M:%S %Y UTC')
    max_date = datetime_to_str(max_date, '%a %b %d %H:%M:%S %Y UTC')
    time_diff = str_from_num(time_diff) + ' ' + time_string
    frequency_tweet = str_from_num(frequency_tweet) + ' tweets/' + time_string.rstrip('s')
    frequency_favorite = str_from_num(frequency_favorite) + '/tweet'
    frequency_retweet = str_from_num(frequency_retweet) + '/tweet'
    global_dialogue = str_from_num(global_dialogue)
    global_sentiment = str_from_num(global_sentiment)
    top_country = str_from_list(top_country)
    top_favorite = str_from_list(top_favorite)
    top_hashtags = str_from_list(top_hashtags)
    top_lang = str_from_list(top_lang)
    top_source = str_from_list(top_source)
    top_url = str_from_list(top_url)
    top_retweet = str_from_list(top_retweet)
    top_usernames = str_from_list(top_usernames)
    top_words = str_from_list(top_words)

    # expand top URL
    # if is_url_shortened(top_url):
        # try: top_url = expand_url(top_url)
        # except: pass

    # remove special characters from tweets text
    top_favorite = '"'+unencode(remove_latin_accents(top_favorite))+'"' if top_favorite else 'None'
    top_retweet = '"'+unencode(remove_latin_accents(top_retweet))+'"' if top_retweet else 'None'

    # analysis overview
    print('\nTweets:', int_tweets, 'from', int_users_tweeting, 'users.'+
          '\nOriginal:', int_original, 'from', int_users_op, 'users.'+
          '\nUsers:', int_users, 'senders and receivers.'+
          '\n\nCountries:', int_country, '(top:', top_country + ').'+
          '\nDialogue:', global_dialogue, 'global.'+
          '\nEmojis:', int_emojis, 'from', int_tweets_with_emoji, 'tweets.'+
          '\nFavorited:', int_global_favorites, '(' + frequency_favorite + ').'+
          '\nGeocodes:', int_tweets_with_geocode, '(' + str(int_geocoded), 'from GeoNames).'+
          '\nHashtags:', int_hashtags, 'from', int_tweets_with_hashtag, 'tweets.'+
          '\nLanguages:', int_lang, '(top:', top_lang.upper() + ').'+
          '\nMedia:', int_media, 'from', int_tweets_with_media, 'tweets.'+
          '\nPlaces:', int_places, 'from', int_tweets_with_place, 'tweets.'+
          '\nRetweeted:', int_global_retweets, '(' + frequency_retweet + ').'+
          '\nSentiment:', global_sentiment, 'global.'+
          '\nSources:', int_sources, '(top:', top_source + ').'+
          '\nURLs:', int_urls, 'from', int_tweets_with_url, 'tweets.'+
          '\nWords:', int_words, 'approximately.'+
          '\n\nRetweets:', int_retweets, 'from', int_users_retweeting, 'senders to', int_users_retweeted, 'receivers.'+
          '\nQuotes:', int_quotes, 'from', int_users_quoting, 'senders to', int_users_quoted, 'receivers.'+
          '\n@-messages:', int_replies, 'from', int_users_replying, 'senders to', int_users_replied, 'receivers.'+
          '\nMentions:', int_mentions, 'from', int_users_mentioning, 'senders to', int_users_mentioned, 'receivers.'+
          '\nInteractions:', int_interactions, 'from', int_users_senders, 'senders to', int_users_receivers, 'receivers.'+
          '\n\nTop words:', top_words+'.'+
          '\nTop hashtags:', top_hashtags+'.'+
          '\nTop users:', top_usernames+'.'+
          '\nTop URL:', top_url+'.'+
          '\nTop retweet:', top_retweet+'.'+
          '\nTop favorite:', top_favorite+'.'+
          '\n\nTime span:', time_diff+'.'+
          '\nFrequency:', frequency_tweet+'.'+
          '\nOldest ID:', str(min_id)+'.'+
          '\nNewest ID:', str(max_id)+'.'+
          '\nSince:', min_date+'.'+
          '\nUntil:', max_date+'.')

def parse_tweets(input_name, quoting=QUOTE_MINIMAL, consider=None,
    time_string='%d/%m/%Y', time_zone=None, geonames=None):
    """
     Analyze output tweets. It is assumed the format is the same of twitter API output.

    Parameters
    ----------
    input_name : str
        The name of .csv/.xlsx file with tweets content.
    quoting : const
        Type of writer uses quote.
    consider : str
	    Name of column. If line contains consider string then this column enters in the parsing process. Else no considers this line.
    time_string: str
	    Specify the format of data. Example: '%d/%m/%Y'.
    time_zone: str
	    Specify the time zone of preference.
    geonames: str
	    Deprecated.

    Returns
    -------
    files : In the same directory returns tops_*.csv, user.csv and location.csv files.

    Raises
    ------
    ReadError
        If file specified in argument input_name don't exist.

    Examples
    --------
    >>> fordpip.parse_tweets('tweets.csv')
    True

    """
    def add_interaction(str_target, str_type):
        # count sent interactions
        dicts_int_sending[str_type][user_name] += 1
        dicts_set_sending[str_type][user_name].add(str_target)
        dicts_set_sending['all'][user_name].add(str_target)
        # count received interactions
        dicts_int_receiving[str_type][str_target] += 1
        dicts_set_receiving[str_type][str_target].add(user_name)
        dicts_set_receiving['all'][str_target].add(user_name)
        # add interacton to network (AT/MT/QT/RT)
        letter = str_type[:1].upper() if str_type != 'reply' else 'A'
        add_to_network(dict_networks[letter+'Ts'],
           [user_name, str_target, str_type, data['id'], data['text'],
           data['favorite_count'], data['rt_count'], data['time']])

    # set default required vars
    delimiter = get_file_delimiter(input_name)
    columns = get_file_header(input_name)
    tz = set_time_zone(time_zone)
    geonames = load_geonames(geonames)
    YourTwapperKeeper = False
    gephi = False

    # check if dataset matches a Gephi edges network
    if all(x in columns for x in ['source', 'target']):
        print('Gephi edges network data found.')
        gephi = True

    # check if dataset matches latest script version
    elif list(columns.keys()) == TWEETS_HEADER:
        print('Up-to-date tweets dataset found.')

    # check if dataset matches YourTwapperKeeper/legacy format
    elif any(i not in columns.keys() for i in ['type', 'media_url', 'place', 'geo_type'])\
    and all(i in columns.keys() for i in YTK_HEADER):
        print('YourTwapperKeeper dataset found.')
        YourTwapperKeeper = True

    # empty time vars
    min_id = None
    max_id = None
    min_timestamp = None
    max_timestamp= None

    # zero int counters
    int_corrupted_lines = 0
    int_duplicate_lines = 0
    int_global_dialogue = 0
    int_global_favorites= 0
    int_global_retweets = 0
    int_global_sentiment = 0
    int_global_users_dialogue = 0

    # empty lists
    # dates = []
    hashtags_by_period = []
    locations = []
    top_dates = []
    top_replies = []
    top_tweets = []
    top_urls = []
    top_users = []
    top_words = []
    top_words_capitalized = []
    users = []
    users_nodes = []
    words_by_period = []

    # empty sets
    set_dates = set()
    set_tids = set()
    set_tweet_ids = set()
    set_users_all = set()
    set_users_tweeting = set()

    # empty dictionaries
    dict_hashtags = {}
    dict_tweets = {}

    # empty list dictionaries
    dict_networks = defaultdict(list)
    dict_capitalized_dates = defaultdict(list)
    dict_emojis_dates = defaultdict(list)
    dict_hashtags_dates = defaultdict(list)
    dict_words_dates = defaultdict(list)
    # dict_lines = defaultdict(list)

    # empty int dictionaries
    dict_int_capitalized = defaultdict(int)
    dict_int_countries = defaultdict(int)
    dict_int_emojis = defaultdict(int)
    dict_int_favorites = defaultdict(int)
    dict_int_hashtags = defaultdict(int)
    dict_int_influence = defaultdict(int)
    dict_int_lang = defaultdict(int)
    dict_int_media = defaultdict(int)
    dict_int_original_tweets = defaultdict(int)
    dict_int_places = defaultdict(int)
    dict_int_quotes = defaultdict(int)
    dict_int_replies = defaultdict(int)
    dict_int_retweets = defaultdict(int)
    dict_int_sentiment = defaultdict(int)
    dict_int_source = defaultdict(int)
    dict_int_text = defaultdict(int)
    dict_int_total = defaultdict(int)
    dict_int_tweets = defaultdict(int)
    dict_int_type = defaultdict(int)
    dict_int_urls = defaultdict(int)
    dict_int_user_favorites = defaultdict(int)
    dict_int_user_retweets = defaultdict(int)
    dict_int_user_tweets = defaultdict(int)
    dict_int_words = defaultdict(int)
    dict_int_words_favorited = defaultdict(int)
    dict_int_words_retweeted = defaultdict(int)
    dict_int_words_favorited_capitalized = defaultdict(int)
    dict_int_words_retweeted_capitalized = defaultdict(int)

    # empty set dictionaries
    dict_set_hashtags = defaultdict(set)
    dict_set_media = defaultdict(set)
    dict_set_urls = defaultdict(set)
    dict_set_tweets_date = defaultdict(set)

    # occurrences by period
    dicts_int_hashtags_by_date = defaultdict(lambda:defaultdict(int))
    dicts_int_words_by_date = defaultdict(lambda:defaultdict(int))

    # tweet, hashtag, sentiment, retweet, reply, quote, mention
    dicts_int_dates = defaultdict(lambda:defaultdict(int))

    # retweet, reply, quote, mention
    dicts_int_receiving = defaultdict(lambda:defaultdict(int))
    dicts_int_sending = defaultdict(lambda:defaultdict(int))

    # retweet, reply, quote, mention, all
    dicts_set_receiving = defaultdict(lambda:defaultdict(set))
    dicts_set_sending = defaultdict(lambda:defaultdict(set))

    print('Parsing tweets...')

    # start file reading
    with open(input_name, 'rt', encoding='utf8') as input_file:
        file_reader = reader(input_file, delimiter=delimiter, quoting=quoting)
        header = next(file_reader) # skips the first line

        with open('users.csv', 'wt', encoding='utf8') as users_file:
            users_writer = writer(users_file, delimiter=delimiter, quoting=quoting)
            users_writer.writerow(TWITTER_USERS_HEADER)

            # iterate through lines
            for line in file_reader:
                time_to_print(file_reader.line_num)
                geo_name = False
                has_emoji = False
                target = None
                sent_value = 0
                # word_pos = 0
                hashtags = set()
                mentions_user = set()
                urls = set()
                words_read = set()
                words_capitalized_read = set()

                # avoid uneven length lines
                if len(line) != len(header):
                    print('Warning: line', str(file_reader.line_num) + ',', 'list index got', len(line), 'and expected', len(header), 'columns.')
                    int_corrupted_lines += 1
                    continue # skip

                elif line == header:
                    print('Warning: line', str(file_reader.line_num) + ',', 'duplicate header.')
                    continue # skip

                try: # analyze
                    data = read_line(line, columns)

                    # avoid duplicates
                    if data['id'] in set_tweet_ids:
                        int_duplicate_lines += 1
                        continue # skip
                    set_tweet_ids.add(data['id'])

                    # parse only tweets containing value
                    if consider and consider in data:
                        if data[consider] == '':
                            continue # skip

                    # get ID range
                    if not min_id or int(data['id']) < min_id:
                        min_id = int(data['id'])
                    if not max_id or int(data['id']) > max_id:
                        max_id = int(data['id'])

                    # timestamp fix
                    if 'timestamp' in columns:
                        data['time'] = data['timestamp']

                    # get timestamp range
                    if not min_timestamp or int(data['time']) < min_timestamp:
                        min_timestamp = int(data['time'])
                    if not max_timestamp or int(data['time']) > max_timestamp:
                        max_timestamp = int(data['time'])

                    # get date
                    date = datetime_from_timestamp(int(data['time']), tz)
                    str_date = datetime_to_str(date, time_string)
                    set_dates.add(str_date)
                    # dates.append(date)

                    # clean line breaks from text
                    for text in ['text', 'rt_text', 'quoted_text']:
                        if text in data: # check for field data first
                            data[text] = data[text].replace('\n', ' ').replace('\r', ' ')

                    # grab full text workaround
                    if data['text'].endswith('…')\
                    and data['text'].startswith('RT @'):
                      try: # expand from retweeted text
                        a,b = data['text'].rstrip('…').split(': ',1)
                        if 'rt_text' in data and data['rt_text'].startswith(b):
                            data['text'] = str(a+': '+data['rt_text'])
                      except: pass

                    if gephi: # expand default values
                        data['hashtags'] = hashtags
                        data['mentions_user'] = mentions_user
                        data['urls'] = urls
                        data['place'] = ''
                        data['country'] = ''
                        data['media_url'] = ''
                        data['created_at'] = ''
                        data['lang'] = 'und'
                        # set matching keys
                        data['id'] = data['tweet_id']
                        data['from_user'] = data['source']
                        # set target if @-message
                        if data['type'] == 'reply':
                            data['reply_to_user'] = data['target']
                        # set target if retweet
                        elif data['type'] == 'retweet':
                            data['rt_user'] = data['target']
                        # set target if quoted
                        elif data['type'] == 'quote':
                            data['quoted_user'] = data['target']
                        # set target if mention
                        elif data['type'] == 'mention':
                            data['mentions_user'] = [data['target']]

                    if YourTwapperKeeper: # expand default values
                        if not 'user_followers' in data:
                            data['user_followers'] = 0
                            data['user_following'] = 0
                        data['hashtags'] = hashtags
                        data['mentions_user'] = mentions_user
                        data['lang'] = 'und'
                        data['urls'] = urls
                        data['rt_id'] = ''
                        data['rt_text'] = data['text']
                        data['rt_count'] = 0
                        data['favorite_count'] = 0
                        data['type'] = 'tweet'
                        # check if classic @-message
                        if data['text'].startswith('@'):
                            data['type'] = 'reply'
                            data['reply_to_user'] = data['text'].split(' ', 1)[0][1:].lower()
                        # check if classic retweet
                        elif data['text'].startswith('RT @'):
                            data['type'] = 'retweet'
                            data['rt_user'] = data['text'].split(':', 1)[0][4:].lower()

                    # lowercase type
                    data['type'] = data['type'].lower()

                    # avoid bugs on legacy datasets
                    if 'rt_text' not in data and int(data['rt_count']) > 0:
                        data['rt_text'] = data['text']

                    # text and sentiment
                    for word in data['text'].split():

                        # word_pos += 1

                        if is_emoji(word):
                            has_emoji = True
                            sent_value += get_emoji_value(word)
                            add_to_dicts(word, dict_int_emojis, dict_emojis_dates, date)

                        elif is_hashtag(word):
                            hashtag = findall(r'(?<=#)[a-zA-Z0-9]+', word)
                            hashtags.add('#'+hashtag[0])\
                                if len(hashtag) == 1 else None

                        elif is_mention(word):
                            mention = findall(r'(?<=@)[a-zA-Z0-9_]+', word)
                            mentions_user.add(mention[0]) if len(mention) == 1 else None

                        elif is_url(word):
                            urls.add(word)

                        else: # common word
                            str_word = clear_word(word)
                            if check_word(str_word):
                                words_read.add(str_word)
                                if word == word.capitalize():
                                    words_capitalized_read.add(str_word.capitalize())

                    if has_emoji:
                        dicts_int_dates['sentiment'][str_date] += sent_value
                        dict_int_sentiment[data['text']] = sent_value
                        dict_int_total['emoji'] += 1
                        int_global_sentiment += sent_value

                    for word in words_read:
                        add_to_dicts(word, dict_int_words, dict_words_dates, date)
                        dict_int_words_favorited[word] += int(data['favorite_count'])
                        dicts_int_words_by_date[str_date][word] += 1

                    for word in words_capitalized_read:
                        add_to_dicts(word.capitalize(), dict_int_capitalized, dict_capitalized_dates, date)
                        dict_int_words_favorited_capitalized[word] += int(data['favorite_count'])

                    # add tweets to dictionary
                    # name = 'ATs' if data['type'] == 'Reply' else 'tweets'
                    # name = 'RTs' if data['type'] == 'Retweet' else name
                    # dict_lines[name].append(line)

                    # get user_name
                    user_name = data['from_user'].lower()
                    set_users_all.add(user_name)

                    # get tweet URL
                    tweet_url = 'https://www.twitter.com/' + user_name + '/status/' + data['id']

                    # add retweet metadata to dictionary
                    tid = data['rt_id'] if 'rt_id' in data else data['id']
                    engagement = int(data['rt_count']) + int(data['favorite_count'])
                    ttext = data['rt_text'] if 'rt_text' in data else data['text']
                    user_posting = data['rt_user'] if 'rt_user' in data else data['from_user']

                    if engagement > 0 and (tid not in set_tids):
                        set_tids.add(tid) # avoid duplicates
                        dict_int_tweets[tid] = engagement
                        dict_tweets[tid] = {'text': ttext,
                                            'from_user': user_posting,
                                            'hashtags': str_from_list(data['hashtags']),
                                            'rt_count': data['rt_count'],
                                            'favorite_count': data['favorite_count'],
                                            'type': data['type'],
                                            'lang': data['lang'],
                                            'place': data['place'],
                                            'country': data['country'],
                                            'source': data['source'],
                                            'media': data['media_url'] if data['media_url'] else data['urls'],
                                            'created_at': data['created_at'],
                                            'url': 'https://www.twitter.com/'+user_posting+'/status/'+tid}

                    # add user metadata to set
                    if user_name not in set_users_tweeting:
                        users_writer.writerow([data.get(i) for i in TWITTER_USERS_HEADER])
                        if not gephi:
                            users_nodes.append([user_name, int(data['user_followers']), int(data['user_following'])])
                        set_users_tweeting.add(user_name)

                    # calculate statistics
                    dicts_int_dates[data['type']][str_date] += 1
                    dict_int_text[ttext] += 1
                    dict_int_lang[data['lang']] += 1
                    dict_int_source[data['source']] += 1
                    dict_int_type[data['type']] += 1
                    dict_int_user_tweets[user_name] += 1
                    dict_set_tweets_date[str_date].add(user_name)

                    # original tweets
                    if data['type'] == 'tweet':
                        # count original tweets
                        dict_int_original_tweets[user_name] += 1
                        # count word retweeted times
                        for word in words_read:
                            dict_int_words_retweeted[word] += int(data['rt_count'])
                        for word in words_capitalized_read:
                            dict_int_words_retweeted_capitalized[word] += int(data['rt_count'])

                    # count retweets and replies
                    if data['type'] in ('retweet', 'reply', 'quote'):
                        target = data['rt_user'] if data['type'] == 'retweet' else data['reply_to_user']
                        target = data['quoted_user'] if data['type'] == 'quote' else target
                        add_interaction(target.lower(), data['type'])
                        set_users_all.add(target.lower())

                    # get retweeted value from Twitter
                    if data['rt_count'] and int(data['rt_count']) > 0:
                        int_global_retweets += int(data['rt_count']) if data['type'] != 'retweet' else 0
                        dict_int_user_retweets[user_name] += int(data['rt_count']) if data['type'] != 'retweet' else 0
                        dict_int_retweets[data['rt_text']] = int(data['rt_count'])

                    # get likes/favorites value from Twitter
                    if data['favorite_count'] and int(data['favorite_count']) > 0:
                        int_global_favorites += int(data['favorite_count'])
                        dict_int_user_favorites[user_name] += int(data['favorite_count'])
                        dict_int_favorites[data['text']] += int(data['favorite_count'])

                    # count mentions
                    if data['mentions_user']:
                        dict_int_total['mention'] += 1
                        mentions_list = str_to_list(data['mentions_user'])

                        for mention in mentions_list:
                            mention = remove_punctuation_special(mention).lower()

                            if mention != target:
                                dicts_int_dates['mention'][str_date] += 1
                                add_interaction(mention, 'mention')
                                set_users_all.add(mention)

                    # count hashtags
                    if data['hashtags']:
                        dict_int_total['hashtag'] += 1
                        hashtags_list = str_to_list(data['hashtags'])
                        valid_hashtags = []

                        for hashtag in hashtags_list:
                            valid_hashtags.append('#'+clear_word(hashtag.lower()))

                        for hashtag in valid_hashtags:
                            dicts_int_dates['hashtag'][str_date] += 1
                            dicts_int_hashtags_by_date[str_date][hashtag] += 1
                            add_to_dicts(hashtag, dict_int_hashtags, dict_hashtags_dates, date, dict_set_hashtags, user_name)
                            add_to_network(dict_networks['hashtags_users'], [user_name, hashtag])

                        for combination in list_combinations(valid_hashtags):
                            add_to_network(dict_networks['hashtags'], [combination[0], combination[1]])

                    # count URLs
                    if data['urls']:
                        dict_int_total['url'] += 1
                        urls_list = str_to_list(data['urls'], separator=', ')\
                            if isinstance(data['urls'], str) else data['urls']
                        for url in urls_list:
                            try: # each
                                url_domain = findall(r'(?<=://)[a-zA-Z0-9_.]+', url)[0].replace('www.','')
                                add_to_dicts(url, dict_int_urls, dict_set=dict_set_urls, item=user_name)
                                add_to_network(dict_networks['URLs_full'], [user_name, url])
                                add_to_network(dict_networks['URLs'], [user_name, url_domain])
                                if any(u in url for u in ['facebook.com', 'fb.me']):
                                    add_to_network(dict_networks['URLs_facebook'], [user_name, url])
                                if any (u in url for u in ['youtube.com', 'youtu.be']):
                                    add_to_network(dict_networks['URLs_youtube'], [user_name, url])
                            except: pass

                    if gephi or YourTwapperKeeper:
                        continue # skip

                    # get most quoted ID
                    if data['type'] == 'quote':
                        dict_int_quotes[data['quoted_text']] += 1

                    # get most replied ID
                    if data['type'] == 'reply':
                        dict_int_replies[data['reply_to_id']] += 1

                    # count embedded media
                    if data['media_url']:
                        dict_int_total['media_url'] += 1
                        add_to_dicts(data['media_url'], dict_int_media, dict_set=dict_set_media, item=user_name)

                    # count location
                    if data['place']:
                        dict_int_total['place'] += 1
                        dict_int_countries[data['country']] += 1
                        dict_int_places[data['place'] + ' (' + data['country'] + ')'] += 1
                        geo_name = data['place'].split(',')[0].replace(',','').replace('-','').lower()
                        ccode = data['country_code'] if 'country_code' in data else None

                    # count geocode locations by Twitter
                    if data['geo_type'].lower() == 'point':
                        dict_int_total['geocode'] += 1
                        # append coordinates to locations output file
                        locations.append([data['latitude'], data['longitude'], 'point', data['place'],
                                          data['country'], ccode, data['lang'], data['time'], data['from_user'],
                                          data['text'], data['user_image_url'], tweet_url])

                    # try and match reverse geocode by country
                    elif geo_name and ccode in geonames.keys()\
                    and geo_name in geonames[ccode].keys():
                        dict_int_total['in_geonames'] += 1
                        latitude, longitude, geoname, = get_geoname(geo_name, geonames, ccode)
                        # append coordinates to locations output file
                        locations.append([latitude, longitude, geoname, data['place'],
                                          data['country'], ccode, data['lang'], data['time'], data['from_user'],
                                          data['text'], data['user_image_url'], tweet_url])

                except Exception as e:
                    print('Warning: line', str(file_reader.line_num) + ',', str(e) + '.')
                    int_corrupted_lines += 1

    int_total_lines = file_reader.line_num
    int_valid_lines = int_total_lines - int_corrupted_lines - int_duplicate_lines - 1

    print('Read', int_total_lines, 'total lines.')
    print(int_corrupted_lines, 'corrupted lines.') if int_corrupted_lines > 0 else None
    print(int_duplicate_lines, 'duplicate tweets.') if int_duplicate_lines > 0 else None
    print(int_valid_lines, 'valid lines.') if int_valid_lines > 0 else None

    if int_valid_lines == 0:
        print('Error: not enough data to parse.')
        return

    # analyze data
    int_tweets = len(set_tweet_ids)
    int_original = dict_int_type['tweet']
    int_quotes = dict_int_type['quote']
    int_retweets = dict_int_type['retweet']
    int_replies = dict_int_type['reply']
    int_mentions = sum(dicts_int_sending['mention'].values())
    int_interactions = int_retweets + int_replies + int_mentions
    int_country = len(dict_int_countries)
    int_emojis = len(dict_int_emojis)
    int_hashtags = len(dict_int_hashtags)
    int_lang = len(dict_int_lang)
    int_media = len(dict_int_media)
    int_places = len(dict_int_places)
    int_sources = len(dict_int_source)
    int_urls = len(dict_int_urls)
    int_words = len(dict_int_words)
    int_geocoded = dict_int_total['in_geonames']
    int_tweets_with_emoji = dict_int_total['emoji']
    int_tweets_with_geocode = dict_int_total['geocode'] + int_geocoded
    int_tweets_with_hashtag = dict_int_total['hashtag']
    int_tweets_with_media = dict_int_total['media_url']
    int_tweets_with_mention = dict_int_total['mention']
    int_tweets_with_place = dict_int_total['place']
    int_tweets_with_url = dict_int_total['url']
    int_users = len(set_users_all)
    int_users_op = len(dict_int_original_tweets)
    int_users_tweeting = len(dict_int_user_tweets)
    int_users_retweeting = len(dicts_set_sending['retweet'])
    int_users_retweeted = len(dicts_set_receiving['retweet'])
    int_users_quoting = len(dicts_set_sending['quote'])
    int_users_quoted = len(dicts_set_receiving['quote'])
    int_users_replying = len(dicts_set_sending['reply'])
    int_users_replied = len(dicts_set_receiving['reply'])
    int_users_mentioning = len(dicts_set_sending['mention'])
    int_users_mentioned = len(dicts_set_receiving['mention'])
    int_users_senders = len(dicts_set_sending['all'])
    int_users_receivers = len(dicts_set_receiving['all'])
    dicts_int_dates['user'] = dict_of_int_from_dict_of_lists(dict_set_tweets_date)

    # unshorten top URLs
    # print('\nUnshortening top 10 URLs...')
    # for url in get_N_first(dict_int_urls, 10):
    #     times_tweeted = dict_int_urls[url]
    #     unique_users = len(dict_set_urls[url])
    #     try: url = expand_url(url) if is_url_shortened(url) else url
    #     except: print('Warning: unable to expand URL ' + url + '.')
    #     else: top_urls.append([url, times_tweeted, unique_users])

    # get a timeline of hashtags
    for hashtag in get_N_first(dict_int_hashtags, 50):
        line = [hashtag]
        for date in sorted(set_dates):
            line.append(dicts_int_hashtags_by_date[date][hashtag])
        hashtags_by_period.append(line)

    # get a timeline of words
    for word in get_N_first(dict_int_words, 50):
        line = [word]
        for date in sorted(set_dates):
            line.append(dicts_int_words_by_date[date][word])
        words_by_period.append(line)

    # get top dates
    for date in set_dates:
        original = dicts_int_dates['tweet'][date]
        retweets = dicts_int_dates['retweet'][date]
        replies = dicts_int_dates['reply'][date]
        quotes = dicts_int_dates['quote'][date]
        tweets = original + retweets + replies
        usernames = dicts_int_dates['user'][date]
        mentions = dicts_int_dates['mention'][date]
        hashtags = dicts_int_dates['hashtag'][date]
        sentiment = dicts_int_dates['sentiment'][date]
        top_dates.append([date, usernames, tweets, original, retweets, replies, mentions, hashtags, sentiment])

    # get top users
    for user in set_users_all:
        # main tweet metadata
        tweets = dict_int_user_tweets[user] if user in dict_int_user_tweets else 0
        rt_count = dict_int_user_retweets[user] if user in dict_int_user_retweets else 0
        favorite_count = dict_int_user_favorites[user] if user in dict_int_user_favorites else 0
        # unique tweet interactions
        qts_in = dicts_int_receiving['quote'][user] if user in dicts_int_receiving['quote'] else 0
        qts_out = dicts_int_sending['quote'][user] if user in dicts_int_sending['quote'] else 0
        rts_in = dicts_int_receiving['retweet'][user] if user in dicts_int_receiving['retweet'] else 0
        rts_out = dicts_int_sending['retweet'][user] if user in dicts_int_sending['retweet'] else 0
        ats_in = dicts_int_receiving['reply'][user] if user in dicts_int_receiving['reply'] else 0
        ats_out = dicts_int_sending['reply'][user] if user in dicts_int_sending['reply'] else 0
        mts_in = dicts_int_receiving['mention'][user] if user in dicts_int_receiving['mention'] else 0
        mts_out = dicts_int_sending['mention'][user] if user in dicts_int_sending['mention'] else 0
        # unique user interactions
        qts_users_in = len(dicts_set_receiving['quote'][user]) if user in dicts_set_receiving['quote'] else 0
        qts_users_out = len(dicts_set_sending['quote'][user]) if user in dicts_set_sending['quote'] else 0
        rts_users_in = len(dicts_set_receiving['retweet'][user]) if user in dicts_set_receiving['retweet'] else 0
        rts_users_out = len(dicts_set_sending['retweet'][user]) if user in dicts_set_sending['retweet'] else 0
        ats_users_in = len(dicts_set_receiving['reply'][user]) if user in dicts_set_receiving['reply'] else 0
        ats_users_out = len(dicts_set_sending['reply'][user]) if user in dicts_set_sending['reply'] else 0
        mts_users_in = len(dicts_set_receiving['mention'][user]) if user in dicts_set_receiving['mention'] else 0
        mts_users_out = len(dicts_set_sending['mention'][user]) if user in dicts_set_sending['mention'] else 0
        # total user/tweet unique interactions
        total_users_in = len(dicts_set_receiving['all'][user]) if user in dicts_set_receiving['all'] else 0
        total_users_out = len(dicts_set_sending['all'][user]) if user in dicts_set_sending['all'] else 0
        total_users = len(set(list(dicts_set_receiving['all'][user]) + list(dicts_set_sending['all'][user])))
        total_in = (rts_in + ats_in + mts_in)
        total_out = (rts_out + ats_out + mts_out)
        total = (total_in + total_out)
        # influence index (user impact)
        if tweets > 0:
            influence = (rts_in/tweets)
            dict_int_influence['@'+user] = influence
            influence = str_from_num(influence)
        else: influence = None
        # dialogue index (@-message intensity)
        if (ats_in+ats_out) > 0:
            dialogue = (ats_out/(ats_in+ats_out))
            int_global_dialogue += dialogue
            dialogue = str_from_num(dialogue)
            int_global_users_dialogue += 1
        else: dialogue = None
        # plurality index (interaction uniqueness)
        plurality = str_from_num(total_users/total) if total > 0 else None
        # add user activity to set
        top_users.append([user, tweets, rt_count, favorite_count,
                          influence, dialogue, plurality,
                          rts_in, rts_users_in, rts_out, rts_users_out,
                          ats_in, ats_users_in, ats_out, ats_users_out,
                          mts_in, mts_users_in, mts_out, mts_users_out,
                          total_in, total_users_in, total_out, total_users_out,
                          total, total_users])

    # get top retweeted tweets
    for tweet_id in get_N_first(dict_int_tweets, 5000):
        text =  dict_tweets[tweet_id]['text']
        from_user = dict_tweets[tweet_id]['from_user']
        hashtags =  dict_tweets[tweet_id]['hashtags']
        rt_count =  dict_tweets[tweet_id]['rt_count']
        favorite_count =  dict_tweets[tweet_id]['favorite_count']
        txt_count = dict_int_text[text] # <== tweet_text counter
        ttype =  dict_tweets[tweet_id]['type']
        lang =  dict_tweets[tweet_id]['lang']
        place =  dict_tweets[tweet_id]['place']
        country =  dict_tweets[tweet_id]['country']
        source =  dict_tweets[tweet_id]['source']
        media =  dict_tweets[tweet_id]['media']
        url =  dict_tweets[tweet_id]['url']
        date =  dict_tweets[tweet_id]['created_at']
        top_tweets.append([text, from_user, tweet_id, hashtags, rt_count, favorite_count,
                           txt_count, ttype, lang, place, country, source, media, date, url])

    # get top words
    for word in get_N_first(dict_int_words, 250):
        times = dict_int_words[word]
        likes = dict_int_words_favorited[word]
        retweets = dict_int_words_retweeted[word]
        top_words.append([word, times, likes, retweets])

    # get top capitalized words
    for word in get_N_first(dict_int_capitalized, 250):
        times = dict_int_capitalized[word]
        gender = gender_identify(word)
        likes = dict_int_words_favorited_capitalized[word]
        retweets = dict_int_words_retweeted_capitalized[word]
        top_words_capitalized.append([word, times, gender, likes, retweets])

    # write datasets by type
    # for key in dict_lines.keys():
        # write_set(('dataset_' + key + '.csv'), dict_lines[key], header)

    header_edges=['type VARCHAR', 'tweet_id VARCHAR', 'text VARCHAR',
        'favorite_count INT', 'rt_count INT', 'time INT']

    for key in dict_networks.keys():
        write_gdf(
            ('network_' + key + '.gdf'),
            dict_networks[key],
            nodes=users_nodes,
            header_nodes=["user_followers INT", "user_following INT"],
            header_edges=header_edges if all(i not in key for i in ['hashtags', 'URLs']) else [],
            directed=True if key != 'hashtags' else False)

    write_set('locations.csv', locations,
        ['latitude', 'longitude', 'geo_type', 'place', 'country', 'country_code', 'lang', 'time', 'user', 'text', 'image_url', 'url'])

    write_set('top_dates.csv', top_dates,
        ['date', 'users', 'tweets', 'original', 'retweets', 'replies', 'mentions', 'hashtags', 'sentiment'])

    write_set('top_tweets.csv', top_tweets,
        ['text', 'from_user', 'tweet_id', 'hashtags', 'rt_count', 'favorite_count', 'tweet_count', 'type', 'lang', 'place', 'country', 'source', 'media', 'date', 'url'])

    # write_set('top_urls_full.csv', top_urls,
        # ['url_full', 'times_tweeted', 'unique_users'])

    write_set('top_users.csv', top_users,
        ['from_user',  'tweets_published', 'retweet_count', 'favorite_count',
         'influence', 'dialogue_%', 'plurality_%',
         'retweets_in', 'retweets_users_in', 'retweets_out', 'retweets_users_out',
         'replies_in', 'replies_users_in', 'replies_out', 'replies_users_out',
         'mentions_in', 'mentions_users_in', 'mentions_out', 'mentions_users_out',
         'total_in', 'total_users_in', 'total_out', 'total_users_out',
         'total', 'total_users'])

    write_set('top_hashtags_by_period.csv', hashtags_by_period,
        ['hashtag']+list(sorted(set_dates)))

    write_set('top_words_by_period.csv', words_by_period,
        ['word']+list(sorted(set_dates)))

    write_set('top_words.csv', top_words,
        ['word', 'times_mentioned', 'likes', 'retweets'])

    write_set('top_words_capitalized.csv', top_words_capitalized,
        ['word', 'times_mentioned', 'name_gender', 'likes', 'retweets'])

    write_values('top_countries.csv', dict_int_countries, ['country', 'tweets', 'tweets_%'], pct=True)
    write_values('top_emojis.UTF16.csv', dict_int_emojis, ['emoji', 'times_tweeted'], encoding='utf16')
    write_values('top_favorites.csv', dict_int_favorites, ['tweet', 'favorite_count'])
    write_values('top_hashtags.csv', dict_int_hashtags, ['hashtag', 'times_mentioned'])
    write_values('top_lang.csv', dict_int_lang, ['lang', 'tweets', 'tweets_%'], pct=True)
    write_values('top_media.csv', dict_int_media, ['media_url', 'times_tweeted'])
    write_values('top_places.csv', dict_int_places, ['place', 'tweets', 'tweets_%'], pct=True)
    write_values('top_quotes.csv', dict_int_quotes, ['tweet', 'times_quoted'])
    write_values('top_replies.csv', dict_int_replies, ['tweet', 'reply_count'])
    write_values('top_retweets.csv', dict_int_retweets, ['tweet', 'rt_count'])
    write_values('top_sentiments.UTF16.csv', dict_int_sentiment, ['tweet', 'sent_value'], encoding='utf16')
    write_values('top_source.csv', dict_int_source, ['source', 'tweets', 'tweets_%'], pct=True)
    write_values('top_text.csv', dict_int_text, ['tweet', 'txt_count'])
    write_values('top_type.csv', dict_int_type, ['type', 'tweets', 'tweets_%'], pct=True)
    write_values('top_URLs.csv', dict_int_urls, ['url', 'times_tweeted'])
    # write_values('top_words.csv', dict_int_words, ['word', 'times_mentioned'])
    # write_values('top_words_liked.csv', dict_int_words_favorited, ['word', 'favorite_count'])
    # write_values('top_words_retweeted.csv', dict_int_words_retweeted, ['word', 'rt_count'])
    # write_values('top_words_capitalized_liked.csv', dict_int_words_favorited_capitalized, ['word', 'favorite_count'])
    # write_values('top_words_capitalized_retweeted.csv', dict_int_words_retweeted_capitalized, ['word', 'rt_count'])

    write_values('top_hashtags_by_users.csv', dict_set_hashtags, ['hashtag', 'unique_users'],
        value_format_function=lambda t: len(t))
    write_values('top_media_by_users.csv', dict_set_media, ['media_url', 'unique_users'],
        value_format_function=lambda t: len(t))
    write_values('top_urls_by_users.csv', dict_set_urls, ['url', 'unique_users'],
        value_format_function=lambda t: len(t))

    ''' # write_timeline() => WIP (work in progress)
    write_timeline('timeline_words_capitalized.csv', dict_capitalized_dates, get_N_first(dict_int_capitalized, 25), dates)
    write_timeline('timeline_words.csv', dict_words_dates, get_N_first(dict_int_words, 25), dates)
    write_timeline('timeline_hashtags.csv', dict_hashtags_dates, get_N_first(dict_int_hashtags, 25), dates)
    write_timeline('timeline_emojis.csv', dict_emojis_dates, get_N_first(dict_int_emojis, 25), dates) '''

    write_wordcloud('wordcloud_words.txt', dict_int_words)
    write_wordcloud('wordcloud_hashtags.txt', dict_int_hashtags)

    # get time range
    min_date = datetime_from_timestamp(min_timestamp, utc=True)
    max_date = datetime_from_timestamp(max_timestamp, utc=True)
    time_diff, time_string, seconds = get_time_diff(max_date, min_date)

    # get frequency
    frequency_tweet = int_tweets/time_diff if time_diff > 0 else 0
    frequency_favorite = int_global_favorites/time_diff if time_diff > 0 else 0
    frequency_retweet = int_global_retweets/time_diff if time_diff > 0 else 0

    # get global values
    global_dialogue = int_global_dialogue/int_global_users_dialogue if int_global_users_dialogue > 0 else 'None'
    global_sentiment = int_global_sentiment/int_tweets_with_emoji if int_tweets_with_emoji > 0 else 'None'

    # get top stats
    top_country = get_N_first(dict_int_countries, 1)[0] if dict_int_countries else 'None'
    top_favorite = get_N_first(dict_int_favorites, 1) if dict_int_favorites else 'None'
    top_hashtags = get_N_first(dict_int_hashtags, 5) if dict_int_hashtags else 'None'
    top_lang = get_N_first(dict_int_lang, 1)[0] if dict_int_lang else 'None'
    top_source = get_N_first(dict_int_source, 1)[0] if dict_int_source else 'None'
    top_url = get_N_first(dict_int_urls, 1) if dict_int_urls else 'None'
    top_retweet = get_N_first(dict_int_retweets, 1) if dict_int_retweets else 'None'
    top_usernames = get_N_first(dict_int_influence, 5) if dict_int_influence else 'None'
    top_words =  get_N_first(dict_int_words, 5) if dict_int_words else 'None'

    # convert to strings
    min_date = datetime_to_str(min_date, '%a %b %d %H:%M:%S %Y UTC')
    max_date = datetime_to_str(max_date, '%a %b %d %H:%M:%S %Y UTC')
    time_diff = str_from_num(time_diff) + ' ' + time_string
    frequency_tweet = str_from_num(frequency_tweet) + ' tweets/' + time_string.rstrip('s')
    frequency_favorite = str_from_num(frequency_favorite) + '/tweet'
    frequency_retweet = str_from_num(frequency_retweet) + '/tweet'
    global_dialogue = str_from_num(global_dialogue)
    global_sentiment = str_from_num(global_sentiment)
    top_country = str_from_list(top_country)
    top_favorite = str_from_list(top_favorite)
    top_hashtags = str_from_list(top_hashtags)
    top_lang = str_from_list(top_lang)
    top_source = str_from_list(top_source)
    top_url = str_from_list(top_url)
    top_retweet = str_from_list(top_retweet)
    top_usernames = str_from_list(top_usernames)
    top_words = str_from_list(top_words)

    # expand top URL
    # if is_url_shortened(top_url):
        # try: top_url = expand_url(top_url)
        # except: pass

    # remove special characters from tweets text
    top_favorite = '"'+unencode(remove_latin_accents(top_favorite))+'"' if top_favorite else 'None'
    top_retweet = '"'+unencode(remove_latin_accents(top_retweet))+'"' if top_retweet else 'None'

    # analysis overview
    print('\nTweets:', int_tweets, 'from', int_users_tweeting, 'users.'+
          '\nOriginal:', int_original, 'from', int_users_op, 'users.'+
          '\nUsers:', int_users, 'senders and receivers.'+
          '\n\nCountries:', int_country, '(top:', top_country + ').'+
          '\nDialogue:', global_dialogue, 'global.'+
          '\nEmojis:', int_emojis, 'from', int_tweets_with_emoji, 'tweets.'+
          '\nFavorited:', int_global_favorites, '(' + frequency_favorite + ').'+
          '\nGeocodes:', int_tweets_with_geocode, '(' + str(int_geocoded), 'from GeoNames).'+
          '\nHashtags:', int_hashtags, 'from', int_tweets_with_hashtag, 'tweets.'+
          '\nLanguages:', int_lang, '(top:', top_lang.upper() + ').'+
          '\nMedia:', int_media, 'from', int_tweets_with_media, 'tweets.'+
          '\nPlaces:', int_places, 'from', int_tweets_with_place, 'tweets.'+
          '\nRetweeted:', int_global_retweets, '(' + frequency_retweet + ').'+
          '\nSentiment:', global_sentiment, 'global.'+
          '\nSources:', int_sources, '(top:', top_source + ').'+
          '\nURLs:', int_urls, 'from', int_tweets_with_url, 'tweets.'+
          '\nWords:', int_words, 'approximately.'+
          '\n\nRetweets:', int_retweets, 'from', int_users_retweeting, 'senders to', int_users_retweeted, 'receivers.'+
          '\nQuotes:', int_quotes, 'from', int_users_quoting, 'senders to', int_users_quoted, 'receivers.'+
          '\n@-messages:', int_replies, 'from', int_users_replying, 'senders to', int_users_replied, 'receivers.'+
          '\nMentions:', int_mentions, 'from', int_users_mentioning, 'senders to', int_users_mentioned, 'receivers.'+
          '\nInteractions:', int_interactions, 'from', int_users_senders, 'senders to', int_users_receivers, 'receivers.'+
          '\n\nTop words:', top_words+'.'+
          '\nTop hashtags:', top_hashtags+'.'+
          '\nTop users:', top_usernames+'.'+
          '\nTop URL:', top_url+'.'+
          '\nTop retweet:', top_retweet+'.'+
          '\nTop favorite:', top_favorite+'.'+
          '\n\nTime span:', time_diff+'.'+
          '\nFrequency:', frequency_tweet+'.'+
          '\nOldest ID:', str(min_id)+'.'+
          '\nNewest ID:', str(max_id)+'.'+
          '\nSince:', min_date+'.'+
          '\nUntil:', max_date+'.')
