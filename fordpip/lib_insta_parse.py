
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from subprocess import call
from os import getcwd, path, chdir
from datetime import datetime

def instagram_parse(args):    
    if not path.exists(args['path_script'] + '/lib/instagram_parse/node_modules/'):
        print('installing the packages!')
        chdir(args['path_script'] + '/lib/instagram_parse')
        call(['npm install'], shell=True)
        chdir(args['path_input'])
    
    params = ['node', args['path_script'] + '/lib/instagram_parse/insta_parse.js']
    params.append(args['input'])

    call(params)