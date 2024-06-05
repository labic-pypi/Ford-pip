#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Set script defaults and behavior. Output logging is automatically enabled and
written to the output file, which can be modified or deactivated on execution.

Quiet (-q) and force (-y) modifiers are available for suppressing or allowing
all future actions without asking, or clone the latest script build on update.

The verbose (-v) modifier provides more detailed output, such as from exception
errors, streaming tweets and trending topics, and updating (requires Git).
'''

from os import chdir, devnull, environ, getpid, remove, walk
from os.path import abspath, dirname, exists, isdir
from platform import architecture, system
from re import findall
from shutil import copy, rmtree
from subprocess import call
from webbrowser import open as web

from .lib_sys import check_cmd, edit, read, unix2dos # less

LANG = environ.get("FORD_LANGUAGE", "english")

__version__ = 'v1.9-rc2'

SSH_KEY = """"""

SSH_PUB = ''

REQUIREMENTS = [x.rstrip() for x in open(f"{dirname(__file__)}/../requirements.txt").readlines()]

def clean(args):
    '''
    Cleanup temporary files left behind.
    '''
    def rm(f):
        try: rmtree(f) if isdir(f) else remove(f)
        except: print('Failed:', f) if args['verbose'] else None
        else: print(f) if args['verbose'] else None

    for (path, dirs, files) in walk(args['path_script']):
        for i in files:
            rm(abspath(path + '/' + i)) if i.endswith('.pyc') else None
        rm(abspath(path)) if path.endswith('__pycache__') else None

    if isdir(args['path_script'] + '/log') and not args['quiet']\
    and (args['force'] or read('Erase log files', confirm=True)):
        for (path, dirs, files) in walk(args['path_script'] + '/log'):
            for i in files:
                rm(abspath(path + '/' + i))
        rm(abspath(path))

    print('Cleanup finished.')

def help(args):
    '''
    Open 'README.md' file for reading.
    '''
    help_file = 'LEIAME.md' if LANG == 'portuguese' else 'README.md'
    help_file = abspath(args['path_script'] + '/' + help_file)
    with open(help_file, 'r') as f:
        for i in f.read().splitlines():
            print(i) if '[' in i else None
    # less(help_file)

def install(args):
    '''
    Install prequesites and create a link to execute script.
    '''
    os = system()

    if os not in ('Linux', 'Windows'):
        print('Error:', os, 'system unsupported.')
        return

    # first link script for execution
    if args['force'] or args['quiet']\
    or read('Confirm '+os+' install', confirm=True):

        script = abspath(args['path_script'] + '/ford.py')

        if os == 'Linux':

            print('Linking "ford" alias to "' + script + '".\n'+\
                  'You may be prompted for your password.\n')

            # create symlink to local binaries folder
            call(['sudo', 'ln', '--symbolic', '--force',
                  script, '/usr/local/bin/ford'])

            # check if successful or not
            if exists('/usr/local/bin/ford'):
                print('Successfully linked to "/usr/local/bin/ford".')

        elif os == 'Windows':

            # check if 32/64-bits
            # x86_64 = architecture()[0][:2]

            uname = check_cmd(['uname'], stdout=True)
            # False => MS-DOS/PowerShell prompt
            # MINGW => Bash (Git/Cmder)
            # MSYS => default Cmder prompt

            if not uname:
              print('Unsupported prompt for aliasing. Skipping...')

            elif uname.startswith('MSYS'):
                # use alias default command
                call(['alias', 'ford=', script, '$*'], shell=True)
                # check if successful or not
                if str('ford='+script+' $*') in check_cmd(['alias']):
                    print('Successfully linked alias to script.')
                else: print('Failed. Trying alternative method...'); uname='MINGW'

            elif uname.startswith('MINGW'):
                # check path for file containing aliases in home folder
                homedrive = findall(r'(?<=HOMEDRIVE=)[a-zA-Z0-9\\/:]+', check_cmd(['env'], stdout=True))[0]
                homepath = findall(r'(?<=HOMEPATH=)[a-zA-Z0-9\\/:]+', check_cmd(['env'], stdout=True))[0]
                profile = abspath(homedrive + homepath.replace('\\', '/') + '/.profile')
                alias = '"py -3 -u ' + script.replace('\\','/') + '"'

                # read whole file contents
                if exists(profile):
                    with open(profile, 'r') as file_input:
                        content = file_input.read().splitlines()
                else: content = [] # empty

                try: # write file contents
                  with open(profile, 'w', encoding='utf8') as file_output:
                    for line in content:
                        file_output.write(line)\
                            if not line.startswith('alias ford=') else None
                    file_output.write('alias ford=' + alias)
                    print('Successfully linked in "' + profile + '".\n'+\
                          'Please restart the script for changes to take in effect.')
                except Exception as e:
                    print(str(e))

    # then install package libraries
    if args['force'] or (not args['quiet']\
    and read('\nInstall required packages', confirm=True)):

        chdir(args['path_script'])
        pip3 = 'pip3' if check_cmd(['pip3', '--version']) else 'pip' # Debian/apt-get
        pip2 = 'pip2' if check_cmd(['pip2', '--version']) else 'pip' # Arch/pacman

        if os == 'Linux':
            # on Debian/Ubuntu derivatives
            if check_cmd(['apt-get', '--version']):
                print('\nUpdating package list...')
                call(['sudo', 'apt-get', 'update'])
                print('\nInstalling packages from repository...')
                call(['sudo', 'apt-get', 'install', 'git', 'openjdk-8-jre', 'python-pip', 'python3-pip',
                      'python-setuptools', 'python3-setuptools', 'python', 'npm', 'r-base', 'openssh-client',
                      # Gooey libraries required for GUI usage listed below
                      'libgtk2.0-dev', 'libgtk-3-dev', 'libjpeg-dev', 'libtiff-dev', 'libsdl1.2-dev', 'libsm-dev',
                      'libnotify-dev', 'freeglut3', 'freeglut3-dev', 'libwebkitgtk-dev', 'libwebkitgtk-3.0-dev',
                      # 'libgstreamer-plugins-base0.10-dev']) # required for older Ubuntu 16.04(.1)
                      'libgstreamer-plugins-base1.0-dev'])
            # on Arch/Antergos derivatives
            elif check_cmd(['pacman', '--version']):
                print('\nUpdating package list...')
                call(['sudo', 'pacman', '-Sy'])
                print('\nInstalling packages from repository...')
                call(['sudo', 'pacman', '-S', 'git', 'python-pip', 'python2-pip', '--needed'])
            # user install Python libraries
            print('\nInstalling Python 3 prequesites...')
            call(['sudo', pip3, 'install', '--user'] + REQUIREMENTS)
            print('\nInstalling Python 2 prequesites...')
            call(['sudo', pip2, 'install', '--user', 'tweepy'])
            # user install npm libraries
            print('\nInstalling npm prequesites...')
            chdir(args['path_script'] + '/lib/hash-collector')
            call(['sudo', 'npm', 'install'])
            chdir(args['path_script'] + '/lib/script_categorias')
            call(['sudo', 'npm', 'install'])
            chdir(args['path_script'] + '/lib/youtube')
            call(['sudo', 'npm', 'install'])
            chdir(args['path_script'] + '/lib/instagram_parse')
            call(['sudo', 'npm', 'install'])

        elif os == 'Windows':
            # get latest Java Runtime Environment from Ninite
            # print('\nInstalling Java RE from Ninite...')
            # user install Python libraries
            print('\nInstalling Python 3 prequesites...')
            call(['py', '-3', '-m', 'pip', 'install', '--user', 'twython', 'pillow', 'requests', 'gooey', 'xlrd'])
            print('\nInstalling Python 2 prequesites...')
            call(['py', '-2', '-m', 'pip', 'install', '--user', 'tweepy'])
            # user install npm libraries
            print('\nInstalling npm prequesites...')
            chdir(args['path_script'] + '/lib/hash-collector')
            call(['npm', 'install'], shell=True)
            chdir(args['path_script'] + '/lib/script_categorias')
            call(['npm', 'install'], shell=True)
            chdir(args['path_script'] + '/lib/youtube')
            call(['npm', 'install'], shell=True)
            chdir(args['path_script'] + '/lib/instagram_parse')
            call(['npm', 'install'], shell=True)

        print('\nFinished installing required packages.'+\
              '\nPlease restart the script for changes to take in effect.')

def uninstall(args):
    '''
    Remove script files and existing alias or
    script link in "/usr/local/bin/ford".
    '''
    os = system()

    if read('Confirm uninstall', confirm=True):

        if os == 'Linux'\
        and exists('/usr/local/bin/ford'):
            call(['sudo', 'rm', '/usr/local/bin/ford'])

        elif os == 'Windows':

            profile = abspath((homedrive + homepath).replace('\\', '/') + '/.profile')

            if check_cmd(['alias']): # works on Cmder
                call(['alias', '/d', 'ford'], shell=True)

            if exists(profile): # works on Bash
                homedrive = findall(r'(?<=HOMEDRIVE=)[a-zA-Z0-9\\/:]+', check_cmd(['env'], stdout=-True))[0]
                homepath = findall(r'(?<=HOMEPATH=)[a-zA-Z0-9\\/:]+', check_cmd(['env'], stdout=-True))[0]

                if exists(profile): # read lines
                    with open(profile, 'r') as file_input:
                        content = file_input.read()
                    with open(profile, 'w', encoding='utf8') as file_output:
                        for line in content.splitlines():
                            if not line.startswith('alias ford='):
                                file_output.write(line)

        if read('Remove script files', confirm=True):
            rmtree(args['path_script'])\

        print('Uninstall finished.')

def update(args):
    '''
    Update script through Git using SSH.
    '''
    def check_key():
        try: # check if SSH key is loaded
            return(SSH_PUB in check_cmd(['ssh-add', '-L'], stdout=True))
        except: return False

    def load_key():
        with open('ford.key', 'w', encoding='utf8') as file:
            file.write(SSH_KEY)
        call(['chmod', '1700', 'ford.key'])
        call(['ssh-add', 'ford.key'], stderr=open(devnull, 'w'))
        remove('ford.key')
        return check_key()

    def load_agent():
        output = check_cmd(['ssh-agent', '-s'], stdout=True)
        ssh_auth_sock = findall(r'(?<=SSH_AUTH_SOCK=)[a-zA-Z0-9/._-]+(?=;)', output)[0] if output else None
        ssh_agent_pid = findall(r'(?<=SSH_AGENT_PID=)[a-zA-Z0-9/._-]+(?=;)', output)[0] if output else None
        # set SSH agent environments
        environ['SSH_AUTH_SOCK'] = ssh_auth_sock
        environ['SSH_AGENT_PID'] = ssh_agent_pid
        return load_key()

    def kill_agent():
        call(['ssh-agent', '-k'], stdout=open(devnull, 'w'), stderr=open(devnull, 'w'))

    def pull():
        chdir(args['path_script'])
        call(['git', 'remote', 'set-url', 'origin', url])
        print('Checking for updates...\n'+
              'Current version:', __version__)\
              if args['verbose'] else None
        if args['force']: # undo changes
            call(['git', 'reset', '--hard'])
        call(['git', 'pull', '--force', url])
        kill_agent() if check_key() else None

    def clone():
        ford_clone = 'ford_' + str(getpid())
        call(['git', 'clone', url, ford_clone])

    # default URL for SSH authentication
    url = 'git@github.com:labic/ford.git'

    if not isdir(args['path_script'] + '/.git'):
        clone() # get whole script from repository

    elif not check_key()\
    and not load_key()\
    and not load_agent():
        print('Error: failed to load SSH identity key.')

    else: pull() # update to latest build

def wiki(args):
    '''
    Open wiki page on default web browser.
    '''
    web('https://bitbucket.org/labic/ford/wiki/Home')
