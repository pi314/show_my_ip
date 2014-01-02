#!/usr/bin/env python
import re
import subprocess as sub

def show_my_ip ():
    ipconfig = sub.check_output(['ipconfig'])
    ipconfig = ipconfig.decode('cp950').encode('utf8').replace('\r\n','\n')
    patt = r'''\n
               (?P<NAME>\S.*?):\n
               \n
               (?:\ \ \ .*?\n)*
               \ \ \ .*?IPv4.*?: (?P<IP>\S*)
            '''
    return dict(m.groups() for m in re.finditer(patt, ipconfig, re.VERBOSE))

if __name__ == '__main__':
    print 'Detected IP addresses:\n'
    for i,j in show_my_ip().iteritems():
        print i + ':'
        print '   ',j
        print ''
