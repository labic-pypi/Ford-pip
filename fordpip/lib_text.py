#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions and constants used to clean
and filter words in texts.  Some characters were not covered
by Python's string.punctuation and were added as needed.

Some third party modules can be used with
this module, if you want to improve it:

* python-nltk for more stopwords;
* rfc3987 to better identify URLS;

The libraries above and others are not currently used to
make the script easier to install for end users.

'''

import string

from .lib_emojis import EMOJIS
from .lib_stopwords import STOPWORDS

VALID_CHARACTERS_SET = set([])

EXTRA_CHARACTERS = "_-"
VALID_CHARACTERS = string.ascii_letters + string.digits
VALID_CHARACTERS = VALID_CHARACTERS + EXTRA_CHARACTERS

for character in VALID_CHARACTERS:
    VALID_CHARACTERS_SET.add(character)

ACCENT_REPLACEMENTS = {
    ord('á'):'a',
    ord('ã'):'a',
    ord('â'):'a',
    ord('à'):'a',
    ord('è'):'e',
    ord('ê'):'e',
    ord('é'):'e',
    ord('í'):'i',
    ord('ì'):'i',
    ord('ñ'):'n',
    ord('ò'):'o',
    ord('ó'):'o',
    ord('ô'):'o',
    ord('õ'):'o',
    ord('ù'):'u',
    ord('ú'):'u',
    ord('ü'):'u',
    ord('ç'):'c'}

UNDESIRED_CHARACTERS = set(string.punctuation)

UNDESIRED_CHARACTERS.add('”')
UNDESIRED_CHARACTERS.add('“')
UNDESIRED_CHARACTERS.add('‘')
UNDESIRED_CHARACTERS.add('…')
UNDESIRED_CHARACTERS.add('—')
UNDESIRED_CHARACTERS.add('|')

UNDESIRED_CHARACTERS_SPECIAL = UNDESIRED_CHARACTERS.copy()
UNDESIRED_CHARACTERS_SPECIAL.remove('_')

intab = ''.join(c for c in UNDESIRED_CHARACTERS)
outtab = ''.join(' ' for c in UNDESIRED_CHARACTERS)
punct_translate_tab = str.maketrans(intab, outtab)

def all_words_in_id(word_list, ids, text_dict):
    '''
    Check if word list present in id.
    '''
    tmp = ''.join(remove_latin_accents(text_word.lower()) + ' ' for text_word in text_dict[ids])
    if all(remove_latin_accents(word['name'].lower()) in tmp for word in word_list):
        return True
    else: return False

def check_word(str_s):
    '''
    Check if string is a valid word or not.
    '''
    word_remove_list = ['rt', '\n', '', 'http', 'https', '//t', '//']
    word_start = ['@', '#', 'co/', '/', 'http']
    word_in = ['kk', 'rsrs', 'haha', '/']
    if len(str_s) > 1\
    and not is_number(str_s)\
    and not is_stopword(str_s)\
    and not any(w in str_s for w in word_in)\
    and not any(str_s.startswith(w) for w in word_start)\
    and not str_s.lower() in word_remove_list:
        return True
    return False

def clear_word(str_s):
    '''
    Clear string from accents and punctuation.
    '''
    str_s = str_s.lower()
    str_s = remove_latin_accents(str_s)
    str_s = remove_punctuation(str_s)
    return str_s

def find_word(word_list, key):
    '''
    Return word if found.
    '''
    for word_obj in word_list:
        if clear_word(word_obj['name']) == clear_word(key):
            return word_obj
    return None

def get_emoji_value(str_s):
    '''
    Return emoji sentiment value.
    '''
    return EMOJIS[str_s]

def get_words(str_s):
    '''
    Get clear valid words from text.
    '''
    valid_words = []
    for word in str_s.split():
        if not is_hashtag(word)\
        and not is_mention(word)\
        and not is_url(word):
            word = clear_word(word)
            valid_words.append(word)\
            if check_word(word) else None
    return valid_words

def has_emoji(str_s):
    '''
    Returns True if the input has an emoji.
    '''
    for key in EMOJIS:
        if key in str_s.split():
            return True
    return False

def is_emoji(str_s):
    '''
    Returns True if the input is an emoji.
    '''
    if str_s in EMOJIS.keys():
        return True
    return False

def is_hashtag(str_s):
    '''
    Returns True if the input is a hashtag.
    '''
    if str_s.startswith("#") and not(str_s.endswith("…")):
        return True
    return False

def is_mention(str_s):
    '''
    Returns True if the input is a mention and False if not.
    A mention is considered here as a string that starts with
    the "@" (at) character.
    '''
    if (str_s.startswith("@") or str_s.startswith("＠")) and not(str_s.endswith("…")):
        return True
    else: return False

def is_number(str):
    '''
    Returns True if the input is a number.
    '''
    try:
        int(str)
        return True
    except Exception:
        try:
            float(str)
            return True
        except Exception:
            return False

def is_stopword(str_s):
    '''
    Returns True if str_s is the stopwords list.
    '''
    if str_s in STOPWORDS:
        return True
    else: return False

def is_url(str_s):
    '''
    Returns True if str_s is an URL.
    '''
    if (str_s.startswith("ht") or str_s.startswith('hr')) and not(str_s.endswith("…")):
        return True
    else: return False

def is_url_shortened(str_s):
    '''
    Returns True if str_s is a shortened URL.
    '''
    if str_s.count('.') == 1 and str_s.split('.')[1].count('/') == 1:
        return True
    else: return False

def remove_invalid_characters(str_s):
    '''
    Removes all characters from a string that aren't
    letters or numbers.
    '''
    list_string_valid_chars = []
    for character in str_s:
        if character in VALID_CHARACTERS_SET:
            list_string_valid_chars.append(character)
    if len(list_string_valid_chars) == 0: return ''
    else: return ''.join(list_string_valid_chars)

def remove_latin_accents(str_s):
    '''
    This function replaces characters with accents
    with non accented characters.
    '''
    return str_s.translate(ACCENT_REPLACEMENTS)

def remove_punctuation(str_s):
    '''
    This function iterates through each character in 'str_s'
    and concatenate them in a new string if it is not in the
    'UNDESIRED_CHARACTERS' set. It returns the given string without
    the UNDESIRED_CHARACTERS, even if it is the empty string.
    '''
    str_clean_string = ''.join(character for character in str_s if character not in UNDESIRED_CHARACTERS)
    if str_clean_string == '': return ''
    else: return str_clean_string

def remove_punctuation_special(str_s):
    '''
    Same as remove_punctuation, except that this preserves the underline character.
    '''
    str_clean_string = ''.join(character for character in str_s if character not in UNDESIRED_CHARACTERS_SPECIAL)
    if str_clean_string == '': return ''
    else: return str_clean_string

def unencode(str_s, encoding='ascii'):
    '''
    Encode and decode string ignoring character errors that might arise.
    '''
    return str_s.encode(encoding, 'ignore').decode()

def process_word(str_s):
    '''
    Word processor with more strict requirements.
    '''
    str_s = str_s.lower()
    str_s = remove_latin_accents(str_s)
    str_s = remove_punctuation(str_s)
    
    word_remove_list = ['rt', '\n', '', 'http', 'https', '//t', '//']
    word_start = ['@', '#', 'co/', '/', 'http']
    word_in = ['kk', 'rsrs', 'haha', '/']
    
    if len(str_s) > 1\
    and not is_number(str_s)\
    and not any(w in str_s for w in word_in)\
    and not any(str_s.startswith(w) for w in word_start)\
    and not str_s.lower() in word_remove_list:
        return str_s

    return None