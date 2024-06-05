#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for loading a
gazetteer dataset file from GeoNames, available at:
the following URL:

http://download.geonames.org/export/dump/

The greater the file size, the more time it will
take to load and parse the geolocation data.
'''

from collections import defaultdict
from csv import reader

from .lib_input import get_file_delimiter

def get_geoname(str_place, geonames, ccode):
    '''
    Find key and value from a dictionary
    loaded by load_geonames() function.
    '''
    latitude = geonames[ccode][str_place][0]
    longitude = geonames[ccode][str_place][1]
    geoname_id = geonames[ccode][str_place][2]
    geoname = 'Approximate (ID ' + geoname_id + ')'
    return latitude, longitude, geoname

def load_geonames(filename):
    '''
    Read a GeoNames gazzetteer file if present and returns a
    list of the data in it, indexed in a dictionary with keys
    as country codes. If no data is in the file, or the file
    is not present, it returns an empty dictionary.
    Download from: <http://download.geonames.org/export/dump/>
    '''
    geonames = defaultdict(dict)
    try: # load list
        delimiter = get_file_delimiter(filename)
        with open(filename, 'rt', encoding='utf8') as csvfile:
            csvfile = reader(csvfile, delimiter=delimiter)
            for line in csvfile:
                geoname_id = line[0]
                name = line[1].lower()
                # ascii_name = line[2]
                # aliases = line[3]
                latitude = str(line[4])
                longitude = str(line[5])
                # feature_class = line[6]
                # feature_code = line[7]
                country_code = line[8]
                # cc2 = line[9]
                # admin1_code = line[10]
                # admin2_code = line[11]
                # admin3_code = line[12]
                # admin4_code = line[13]
                # population = line[14]
                # elevation = line[15]
                # dem = line[16]
                # timezone = line[17]
                # modification_date = line[18]
                geonames[country_code][name] = (latitude, longitude, geoname_id)
        country_codes = len(geonames) # count number of countries considered
        print('Loaded', country_codes, 'gazetteer' + ('s' if country_codes>1 else '') + '.')
    except: geonames = {}
    return geonames