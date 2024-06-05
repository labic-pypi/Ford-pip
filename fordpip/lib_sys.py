#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
This module contains functions for logging output, unpacking
files, raising custom exceptions and converting line breaks.
'''

import sys, tarfile, zipfile

from csv import field_size_limit
from datetime import datetime
from errno import ENOENT
from os import chdir, devnull, getenv, getpid, listdir, makedirs, strerror
from os.path import abspath, isdir, isfile, splitext
from platform import system
from subprocess import call, check_output
from time import time
from webbrowser import open as webbrowser_open

class Logger(object):
    '''
    Log printed output to file.
    '''
    def __init__(self, log_file, mode='a'):
        self.log = open(log_file, mode)

    def __del__(self): # restore
        sys.stdout = sys.__stdout__
        sys.stdin = sys.__stdin__
        sys.stderr = sys.__stderr__
        self.log.close()

    def write(self, data):
        self.log.write(data)
        self.log.flush()
        sys.__stdout__.write(data)
        sys.__stdout__.flush()

    def readline(self):
        s = sys.__stdin__.readline()
        sys.__stdin__.flush()
        self.log.write(s)
        self.log.flush()
        return s

    def flush(foo):
        return

def check_cmd(cmd, stdout=True):
    '''
    Check if command results in error or is successful.
    '''
    shell = True if system() == 'Windows' else False
    try: var = check_output(cmd, stderr=open(devnull, 'w'), shell=shell)
    except: return False
    if stdout: # printed message
        return var.decode('utf8')
    return True

def check_file(input_name):
    '''
    Check if file exists or raise error if not.
    '''
    if not isfile(input_name):
        file_error(input_name)

def edit(file_name, editor=None):
    '''
    Open file for editing according to OS.
    '''
    default = ['gedit', 'kate', 'pluma', 'mousepad', 'nano', 'notepad']

    if not editor: # get from environment
        editor = getenv('EDITOR')

    if editor: # user or environment set
        call([editor, file_name])

    else:  # fallback
        for e in default:
            try: call([e, file_name])
            except FileNotFoundError:
                pass # ignore
            except KeyboardInterrupt:
                raise # interrupt
            else: return
        # try again if unsuccessful
        webbrowser_open(file_name)

def exception(e, log=False, verbose=True):
    '''
    Show exception error information in an orderly fashion.
    '''
    def excepthook(err_type, err_value, err_traceback):
        # from traceback import print_tb
        print('Type:', err_type, '\nValue:', err_value)
        # print_tb(err_traceback)
    if not verbose: # custom traceback
        sys.excepthook = excepthook
    if log == True: # default log name
        log = 'exception_'+str(getpid())+'.txt'
    if isinstance(log, str): # write to log file
        sys.stdout = sys.stderr = sys.stdin = Logger(log, 'a')
    print('Error: failed to execute script.')
    raise(e)

def exception_line(e, line_num, verbose=False):
    '''
    Show exception error in a line.
    '''
    print('Warning: line', str(file_reader.line_num) + ',', str(e) + '.')
    if verbose: exception(e)

def file_error(input_name):
    '''
    Return file not found exception when executed.
    '''
    raise FileNotFoundError(ENOENT, strerror(ENOENT), input_name)

def less(file_name, line='+0'):
    '''
    Open file for viewing.
    '''
    call(['less', line, '-P', 'Press Q to quit or / to search for word', file_name], shell=False)

def list_path(path, files=True, absolute=False, folders=False,
              names=False, hidden=False, ignore=[], ext=[]):
    '''
    List content files and folders in a specific directory,
    either as absolute paths, names or folders only.
    '''
    list_of_contents = []
    for f in sorted(listdir(path)):
        absf = abspath(path+'/'+f)
        if ((files and isfile(absf))\
            or (folders and isdir(absf)))\
        and (not ext\
            or any(f.endswith('.'+e.lstrip('.')) for e in ext))\
        and (not ignore\
            or (not any(f.startswith(e) for e in ignore)\
            and not any(f.endswith(e) for e in ignore)))\
        and (hidden\
            or not f.startswith('.')):
                f = splitext(f)[0] if names else\
                    (absf if absolute else f)
                list_of_contents.append(f)
    return list_of_contents

def max_field_size_limit(d=10):
    '''
    Avoid field limit errors when reading CSV files
    by setting the max field size to maximum allowed.
    On Windows, the value is divided by 10 (default)
    until it is successful in setting the limit.
    '''
    max_size = int(sys.maxsize)

    while True:
        max_size = int(max_size/d)
        try: field_size_limit(max_size)
        except: pass
        else: return#(max_size)

def max_user_size_limit(d=10):
    '''
    Workaround to avoid memory user limit errors.
    Tested on Linux and Mac; Windows/WSL Bash untested.
    '''
    try: call(['ulimit', '-s', '-H'], stdout=open(devnull, "w"))
    except FileNotFoundError: pass

def mkpath(path, cd=False, append_date=False, date_str='%b %d'):
    '''
    Create output path according to arguments provided.
    '''
    if append_date:
        date = datetime.fromtimestamp(time()).strftime(date_str)
        date_str = ' (' + str(date) + ')'
        path = path + date_str

    while True:
        try: # create path
            makedirs(path)
        except: # append process ID
            pid_str = ' [' + str(getpid()) + ']'
            path = path + pid_str
        else: # change dir and return string
            chdir(path) if cd else None
            return path

def read(q, opt=[], opt_desc=[], opt_hidden=[], default=None, confirm=False, optional=False):
    '''
    Set specified argument by asking user or through a set of choices.
    '''
    def ask():
        print(q+':', end='')
        if any(x and x != opt_hidden for x in [opt, opt_desc]):
            print() # jump a line
            for number, option in enumerate(opt_desc):
                print(str(number + 1) + '. ' + option)
            print('>', end='') # mark answer
        return input(' ')

    def choose():
        if str(var) in opt:
            return str(var)
        try: # check inbetween options
            if 0 < int(var) <= len(opt):
                return str(opt[int(var)-1])
            else: return ''
        except: return ''

    def more():
        for number, title in enumerate(opt_hidden):
            title = title.encode('utf-8', 'ignore').decode('ascii', 'ignore')
            print(str(number + 1) + '. ' + str(title))

    def true_false():
        var = input(q + '? [y/N] ')
        if var[0:1].lower() == 'y':
            return True
        return False

    def error():
        e = "Error: missing or invalid argument.\n"+\
            "Run -h or --help for documentation."
        quit(e)

    for i in [opt_desc, opt_hidden]:
        if i and not opt:
            opt = i

    if not isinstance(opt, list):
        opt = list(opt)


    while True:

        try: # ask user for input

            var = true_false()\
                  if confirm\
                  else ask()

            if opt_hidden\
            and var == '?':
                more(); print()

            else: print(); break

        except (KeyboardInterrupt, EOFError) as e:
            print('\n'); error()

    if (var != '' and opt != []):
        var = choose()

    if (var == ''):
        if default:
            return default
        elif optional:
            return None
        else: error()

    return var

def unix2dos(filename):
    '''
    Convert line breaks to MS-DOS format,
    fixing for instance the CLRF bug on Notepad.
    '''
    try: call(['unix2dos', filename], stderr=open(devnull, 'w'))
    except FileNotFoundError: pass

def untar(file_name, path='.'):
    '''
    Extract a tar file.
    '''
    print('Extracting...')
    tar = tarfile.open(file_name)
    tar.extractall(path=path)
    tar.close()

def unzip(file_name, path='.'):
    '''
    Extract a zip file.
    '''
    print('Extracting...')
    with zipfile.ZipFile(file_name) as z:
        z.extractall(path=path)