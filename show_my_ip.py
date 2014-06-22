#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess as sub
import os
import sys

VERSION = sys.version_info[0]
RUN_IN_WINDOWS = os.uname()[0].startswith('CYGWIN_NT')

def show_my_ip_ipconfig ():
    ipconfig = str(sub.check_output(['ipconfig']))
    ipconfig = ipconfig.decode('cp950').encode('utf8').replace('\r\n','\n')
    patt = r'''\n
               (?P<NAME>\S.*?):\n
               \n
               (?:\ \ \ .*?\n)*
               \ \ \ .*?IPv4.*?:\ *(?P<IP>\S*)
            '''
    return dict(m.groups() for m in re.finditer(patt, ipconfig, re.VERBOSE))

def show_my_ip_ifconfig ():
    if VERSION == 3:
        ifconfig = str(sub.getoutput(['ifconfig']))#.decode('utf-8')
    else:
        ifconfig = str(sub.check_output(['ifconfig']))#.decode('utf-8')
    patt = r'''(?P<NAME>\w+):\ flags.*\n
               (?:\s+.*?\n)*
               \s+inet\ (?P<IP>.*)\ netmask.*
            '''
    return dict(m.groups() for m in re.finditer(patt, ifconfig, re.VERBOSE))

def show_my_ip ():
    if RUN_IN_WINDOWS:
        return show_my_ip_ipconfig()
    return show_my_ip_ifconfig()

if __name__ == '__main__':

    print('Python version %d detected.'%(VERSION))
    if VERSION == 3 and RUN_IN_WINDOWS:
        print('This program is not supported in "Python3 in Cygwin", use Python2 insteed.')
        print('Sorry for the inconvenience.')
        exit()

    print('Detected IP addresses:\n')
    result = show_my_ip()
    for i in result:
        print(i + ':')
        print('   ', result[i])
        print('')
