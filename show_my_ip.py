#!/usr/bin/env python
from __future__ import print_function
import re
import subprocess as sub
import os
import sys

PYTHON_VERSION = sys.version_info[0]
PLATFORM = sys.platform

class NetworkInterface ():

    def __init__ (self, name):
        self.name = name
        self.ip_addr     = ''
        self.mac_addr    = ''
        self.netmask_hex = ''
        self.netmask_ip  = ''
        self.netmask_len = 0

    def set_ip (self, ip_addr):
        self.ip_addr = ip_addr

    def set_mac_addr (self, mac_addr):
        self.mac_addr = mac_addr

    def set_netmask (self, netmask):
        if netmask.startswith('0x'):
            self.netmask_hex = netmask[2:]
            self.netmask_len = bin( int(netmask, 16) ).count('1')
            self.netmask_ip  = '.'.join(
                map(
                    lambda x:str(int(''.join(x), 16)),
                    zip(netmask[2::2], netmask[3::2])
                )
            )

    def __str__ (self):
        return '<NetworkInterface: '+\
            self.name +'('+ self.mac_addr +') '+\
            self.ip_addr +'/'+ str(self.netmask_len) +'>'

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

def show_my_ip_ifconfig_freebsd ():

    if PYTHON_VERSION == 3:
        ifconfig_output = str(sub.getoutput(['ifconfig']))
    else:
        ifconfig_output = str(sub.check_output(['ifconfig']))

    ret = list()

    for i in ifconfig_output.splitlines():
        if i.strip() == '':
            continue

        if i[0] != ' ':
            nic = NetworkInterface(i.split(':')[0])
            ret.append(nic)

        i = i.strip()

        if i.startswith('ether'):
            nic.set_mac_addr(i.split()[1])

        if i.startswith('inet '):
            i = i.split()
            packet = dict(zip(i[::2], i[1::2]))

            if 'inet' in packet:
                nic.set_ip(packet['inet'])

            if 'netmask' in packet:
                nic.set_netmask(packet['netmask'])

    return ret

def show_my_ip ():
    if PYTHON_VERSION == 3 and PLATFORM == 'cygwin':
        print('This program is not supported in "Python3 in Cygwin", use Python2 insteed.',
            file=sys.stderr)
        print('Sorry for the inconvenience.',
            file=sys.stderr)
        return ()

    if PLATFORM == 'cygwin':
        return show_my_ip_ipconfig()

    elif PLATFORM.startswith('freebsd'):
        return show_my_ip_ifconfig_freebsd()

    else: # guess the system is GNU-Linux-based
        return show_my_ip_ifconfig_linux()

if __name__ == '__main__':

    print('Detected Network Interfaces:\n')
    result = show_my_ip()
    for nic in result:
        print( '{} : {}'.format(nic.name, nic.mac_addr) )
        print( '   {}/{}'.format(nic.ip_addr, nic.netmask_len) )
        print( '' )
