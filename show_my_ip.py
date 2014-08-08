#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
        self.gateway     = ''

    def set_ip_addr (self, ip_addr):
        self.ip_addr = ip_addr

    def set_mac_addr (self, mac_addr):
        self.mac_addr = mac_addr.strip()

    def set_netmask (self, netmask):
        if netmask.startswith('0x'):
            self.netmask_hex = netmask
            self.netmask_len = bin( int(netmask, 16) ).count('1')
            self.netmask_ip  = '.'.join(
                map(
                    lambda x:str(int(''.join(x), 16)),
                    zip(netmask[2::2], netmask[3::2])
                )
            )
        elif netmask.count('.') == 3:
            self.netmask_ip  = netmask
            netmask_int_list = map(int, netmask.split('.') )
            self.netmask_len = ''.join(
                map(bin,  netmask_int_list)
            ).count('1')
            self.netmask_hex = '0x' + ''.join(
                map(lambda x: hex(x)[2:].zfill(2), netmask_int_list)
            )
        else:
            self.raw_netmask = netmask

    def set_gateway (self, gateway):
        self.gateway = gateway

    def __str__ (self):
        return '<NetworkInterface: '+\
            self.name +'('+ self.mac_addr +') '+\
            self.ip_addr +'/'+ str(self.netmask_len) +'>'

def show_my_ip_ipconfig (all):

    if PYTHON_VERSION == 3:
        ipconfig_output = sub.check_output(['ipconfig', '/all'])
        import codecs
        ipconfig_output = codecs.decode(bytes(ipconfig_output), 'cp950' )
    else:
        ipconfig_output = str(sub.check_output(['ipconfig', '/all']))
        ipconfig_output = ipconfig_output.decode('cp950').encode('utf8')

    ret = []

    for i in ipconfig_output.splitlines():
        if i.strip() == '':
            continue

        if i.startswith('Windows IP 設定'):
            continue

        if i[0] != ' ':
            nic = NetworkInterface(i.split(':')[0])
            ret.append(nic)

        i = i.strip()

        if i.startswith('實體位址'):
            nic.set_mac_addr( i[i.find(':')+2:] )

        if i.startswith('IPv4'):
            nic.set_ip_addr( i[i.find(':')+2 : i.find('(')] )

        if i.startswith('子網路遮罩'):
            nic.set_netmask( i[i.find(':')+2:] )

        if i.startswith('預設閘道'):
            nic.set_gateway( i[i.find(':')+2:] )

    if not all:
        return filter(lambda x:x.netmask_len!=0, ret)
    return ret

def show_my_ip_ifconfig_freebsd (all):

    if PYTHON_VERSION == 3:
        ifconfig_output = str(sub.getoutput(['ifconfig']))
    else:
        ifconfig_output = str(sub.check_output(['ifconfig']))

    ret = list()

    for i in ifconfig_output.splitlines():
        if i.strip() == '':
            continue

        if i[0] not in  [' ', '\t']:
            nic = NetworkInterface(i.split(':')[0])
            ret.append(nic)

        i = i.strip()

        if i.startswith('ether'):
            nic.set_mac_addr(i.split()[1])

        if i.startswith('inet '):
            i = i.split()
            packet = dict(zip(i[::2], i[1::2]))

            if 'inet' in packet:
                nic.set_ip_addr(packet['inet'])

            if 'netmask' in packet:
                nic.set_netmask(packet['netmask'])

    if not all:
        return filter(lambda x:x.netmask_len!=0, ret)
    return ret

def show_my_ip_ifconfig_linux (all):

    if PYTHON_VERSION == 3:
        ifconfig_output = str(sub.getoutput(['ifconfig']))
    else:
        ifconfig_output = str(sub.check_output(['ifconfig']))

    ret = list()

    for i in ifconfig_output.splitlines():
        if i.strip() == '':
            continue

        if i[0] != ' ':
            nic = NetworkInterface(i.split(' ')[0])
            if 'HWaddr' in i:
                nic.set_mac_addr( i[ i.find('HWaddr')+7:] )
            ret.append(nic)

        i = i.strip()

        if i.startswith('inet '):
            i = i.split()[1:]
            packet = dict( map(lambda x:tuple(x.split(':')), i) )

            if 'addr' in packet:
                nic.set_ip_addr(packet['addr'])

            if 'Mask' in packet:
                nic.set_netmask(packet['Mask'])

    if not all:
        return filter(lambda x:x.netmask_len!=0, ret)
    return ret

def show_my_ip (all=False):
    # Yes, I know I just overrided the built-in function ``all``, but I know I won't use it.

    if PLATFORM == 'cygwin':
        return show_my_ip_ipconfig(all)

    elif PLATFORM.startswith('freebsd'):
        return show_my_ip_ifconfig_freebsd(all)

    else: # guess the system is GNU-Linux-based
        return show_my_ip_ifconfig_linux(all)

if __name__ == '__main__':

    print('Detected Network Interfaces:\n')
    #result = show_my_ip(all=True)
    result = show_my_ip()
    for nic in result:
        print( '{}: {}'.format(nic.name, nic.mac_addr) )
        print( '    IP/Mask: {}/{}'.format(nic.ip_addr, nic.netmask_len) )
        if nic.gateway != '':
            print( '    Gateway: {}'.format(nic.gateway) )
        print( '' )
