#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import subprocess as sub
import os
import sys

PYTHON_VERSION = sys.version_info[0]
PLATFORM = sys.platform

class NetworkInterface ():

    def __init__ (self, name):
        self.name = name
        self.ip_addr     = []
        self.mac_addr    = ''
        self.netmask_hex = []
        self.netmask_ip  = []
        self.netmask_len = []
        self.gateway     = []

    def add_ip_addr (self, ip_addr):
        self.ip_addr.append(ip_addr)

    def set_mac_addr (self, mac_addr):
        self.mac_addr = mac_addr.strip()

    def add_netmask (self, netmask):
        if netmask.startswith('0x'):
            self.netmask_hex.append( netmask )
            self.netmask_len.append( bin( int(netmask, 16) ).count('1') )
            self.netmask_ip.append(  '.'.join(
                    map(
                        lambda x:str(int(''.join(x), 16)),
                        zip(netmask[2::2], netmask[3::2])
                    )
                ) )
        elif netmask.count('.') == 3:
            self.netmask_ip.append(  netmask )
            netmask_int_list = map(int, netmask.split('.') )
            self.netmask_len.append( ''.join(
                map(bin,  netmask_int_list)
            ).count('1') )
            self.netmask_hex.append( '0x' + ''.join(
                map(lambda x: hex(x)[2:].zfill(2), netmask_int_list)
            ) )

    def add_gateway (self, gateway):
        self.gateway.append( gateway )

    def __str__ (self):
        return '<NetworkInterface: {name}({mac}) {ip}/{mask}'.format(
            name=self.name,
            mac=self.mac_addr,
            ip=self.ip_addr,
            mask=self.netmask_len,
        )

def get_nic_info_ipconfig (all):

    ipconfig_command = ['/cygdrive/c/Windows/System32/ipconfig', '/all']
    if PYTHON_VERSION == 3:
        ipconfig_output = sub.check_output(ipconfig_command)
        import codecs
        ipconfig_output = codecs.decode(bytes(ipconfig_output), 'cp950' )
    else:
        ipconfig_output = str(sub.check_output(ipconfig_command))
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

        elif i.startswith('IPv4'):
            nic.add_ip_addr( i[i.find(':')+2 : i.find('(')] )

        elif i.startswith('子網路遮罩'):
            nic.add_netmask( i[i.find(':')+2:] )

        elif i.startswith('預設閘道'):
            nic.add_gateway( i[i.find(':')+2:] )

    if not all:
        return filter(lambda x:x.netmask_len!=0, ret)

    return ret

def get_nic_info_ifconfig (all):

    if PYTHON_VERSION == 3:
        ifconfig_output = str( sub.check_output(['ifconfig']), 'utf-8' )
    else:
        ifconfig_output = str( sub.check_output(['ifconfig']) )

    ret = list()

    for raw_line in ifconfig_output.splitlines():
        line = raw_line.strip()
        if raw_line.strip() == '':
            continue

        if raw_line[0] not in (' ', '\t'):
            nic = NetworkInterface( line.split()[0].strip(':') )
            ret.append(nic)

        if line.startswith('ether'):
            nic.set_mac_addr( line.split()[1] )

        if 'HWaddr' in line:
            nic.set_mac_addr( line.split()[-1] )

        if line.startswith('inet '):
            if ':' in line:
                # Maybe it's Linux Mint 16
                for word in line.split():
                    if 'addr' in word:
                        nic.add_ip_addr( word.split(':')[1] )
                    elif 'Mask' in word:
                        nic.add_netmask( word.split(':')[1] )
            else:
                # Maybe it's FreeBSD or Arch Linux
                words = line.split()
                nic.add_ip_addr( words[1] )
                nic.add_netmask( words[3] )

    if not all:
        return filter(lambda x:x.netmask_len!=0, ret)
    return ret

def get_nic_info (all=False):
    # Yes, I know I just overrided the built-in function ``all``, but I know I won't use it.

    if PLATFORM == 'cygwin':
        return get_nic_info_ipconfig(all)

    return get_nic_info_ifconfig(all)

def output (all=False):
    print('Detected Network Interfaces:\n')
    result = get_nic_info(all)
    for nic in result:
        print( '{}: {}'.format(nic.name, nic.mac_addr) )
        for i in zip(nic.ip_addr, nic.netmask_len):
            print( '    IP/Mask: {}/{}'.format(*i) )
        for i in nic.gateway:
            print( '    Gateway: {}'.format(i) )
        print( '' )

if __name__ == '__main__':
    output(all=len(sys.argv) > 1 and sys.argv[1] in ('-a', '--all'))
