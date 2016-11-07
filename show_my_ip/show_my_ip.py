#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function
import argparse
import importlib
import importlib.util
import os
import re
import subprocess as sub
import sys

_PYTHON_VERSION = sys.version_info[0]
_PLATFORM = sys.platform

netmask_dec_pattern = re.compile(r'^(\d{1,3}).(\d{1,3}).(\d{1,3}).(\d{1,3})$')


class NetworkInterface:
    def __init__(self, name, cidr):
        self.name = name
        self.ip_set = set()
        self.mac_addr = ''
        self.gateways = set()
        self.cidr = cidr

    def add_ip_addr(self, ip_addr, netmask):
        if netmask.startswith('0x'):
            netmask_int = int(netmask, 16)
        else:
            m = netmask_dec_pattern.match(netmask)
            if m:
                a = int(m.group(1))
                b = int(m.group(2))
                c = int(m.group(3))
                d = int(m.group(4))
                netmask_int = (a << 24 | b << 16 | c << 8 | d)

        if self.cidr:
            self.ip_set.add((ip_addr, bin(netmask_int).count('1')))
        else:
            a = str(netmask_int >> 24)
            b = str((netmask_int >> 16) & 0xff)
            c = str((netmask_int >> 8) & 0xff)
            d = str((netmask_int & 0xff))
            self.ip_set.add((ip_addr, '.'.join((a, b, c, d))))

    def set_mac_addr(self, mac_addr):
        self.mac_addr = mac_addr.strip()

    def add_gateway(self, gateway):
        self.gateways.add(gateway)

    def __str__(self):
        return '<NetworkInterface: {name}({mac})'.format(
            name=self.name,
            mac=self.mac_addr,
        )

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return id(self.name)


def get_ifconfig_output():
    if _PYTHON_VERSION == 3:
        return str(sub.check_output(['ifconfig']), 'utf-8')
    else:
        return str(sub.check_output(['ifconfig']))


def get_nic_info_netifaces(show_all, cidr, data):
    import netifaces

    data['src'] += ', netifaces'
    for nic_name in netifaces.interfaces():
        info = netifaces.ifaddresses(nic_name)
        if netifaces.AF_INET in info:
            if nic_name not in data['info']:
                nic = NetworkInterface(nic_name, cidr)
                data['info'][nic_name] = nic

            else:
                nic = data['info'][nic_name]

            if netifaces.AF_LINK in info:
                nic.set_mac_addr(info[netifaces.AF_LINK][0]['addr'])

            for addr in info[netifaces.AF_INET]:
                nic.add_ip_addr(addr['addr'], addr['netmask'])

    if not show_all:
        rid = {name for name, nic in data['info'].items() if not len(nic.ip_set)}
        for name in rid:
            del data['info'][name]


def get_nic_info_ipconfig(show_all, cidr, cygwin):
    if cygwin:
        ipconfig_command = ['/cygdrive/c/Windows/System32/ipconfig', '/all']
    else:
        ipconfig_command = ['c://Windows/System32/ipconfig', '/all']

    if _PYTHON_VERSION == 3:
        ipconfig_output = sub.check_output(ipconfig_command)
        import codecs
        ipconfig_output = codecs.decode(bytes(ipconfig_output), 'cp950')
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
            nic.set_mac_addr(i[i.find(':')+2:])

        elif i.startswith('IPv4'):
            nic.add_ip_addr(i[i.find(':')+2:i.find('(')])

        elif i.startswith('子網路遮罩'):
            nic.add_netmask(i[i.find(':')+2:])

        elif i.startswith('預設閘道'):
            nic.add_gateway(i[i.find(':')+2:])

    if not show_all:
        return {name: nic for name, nic in ret.items() if len(nic.ip_set)}

    return ret


def get_nic_info_ifconfig(show_all, cidr):
    ifconfig_output = get_ifconfig_output()

    ret = {}
    nic_name_pattern = re.compile(r'^([^:\s]+).*')
    mac_addr_pattern = re.compile(r'.*(?:HWaddr|ether)\s+([0-9a-fA-F]{2}(?::[0-9a-fA-F]{2}){5}).*')
    for line in ifconfig_output.splitlines():
        if line.strip() == '':
            continue

        m = nic_name_pattern.match(line)
        if m:
            nic_name = m.group(1)
            nic = NetworkInterface(nic_name, cidr)
            ret[nic_name] = nic

        m = mac_addr_pattern.match(line)
        if m:
            nic.set_mac_addr(m.group(1))

        m = re.match(r'^\s+inet addr:([^\s]+)\s+.*Mask:([^\s]+)$', line)
        if m:
            # It's Linux Mint 16
            nic.add_ip_addr(m.group(1), m.group(2))

        m = re.match(r'^\s+inet\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+netmask\s+(0x[0-9a-fA-F]{8}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*$', line)
        if m:
            # It's FreeBSD, Arch Linux or Mac OS X
            nic.add_ip_addr(m.group(1), m.group(2))

    if not show_all:
        return {name: nic for name, nic in ret.items() if len(nic.ip_set)}

    return ret


def get_nic_info(show_all=False, cidr=False):
    v = os.environ.get('VIRTUAL_ENV', None)
    if v:
        # hardcoded "3.5" should be fixed
        sys.path = [v + '/lib/python3.5/site-packages'] + sys.path

    ret = {}

    if _PLATFORM == 'cygwin':
        ret = {
            'src': 'ipconfig (cygwin)',
            'info': get_nic_info_ipconfig(show_all, cidr),
        }

    elif _PLATFORM == 'win32':
        ret =  {
            'src': 'ipconfig',
            'info': get_nic_info_ipconfig(show_all, cidr, cygwin),
        }

    else:
        ret = {
            'src': 'ifconfig',
            'info': get_nic_info_ifconfig(show_all, cidr),
        }

    if importlib.util.find_spec('netifaces'):
        get_nic_info_netifaces(show_all, cidr, ret)

    return ret


def output(show_all=False, cidr=False):
    result = get_nic_info(show_all=show_all, cidr=cidr)
    print('Detected Network Interfaces: ({})\n'.format(result['src']))
    for nic_name, nic in sorted(result['info'].items(), key=lambda x: x[0]):
        print('{}: ({})'.format(nic.name, nic.mac_addr))
        for ip, mask in nic.ip_set:
            print('    IP/Mask: {}/{}'.format(ip, mask))
        for i in nic.gateways:
            print('    Gateway: {}'.format(i))

        print('')


def main():
    parser = argparse.ArgumentParser(description='Show my IP')
    parser.add_argument('-a', '--all', action='store_true', dest='show_all',
        help='show all interfaces')
    parser.add_argument('-C', '--no-cidr', action='store_false', dest='cidr',
        help='Don\'t show netmask in CIDR notation')

    args = parser.parse_args()
    output(show_all=args.show_all, cidr=args.cidr)


if __name__ == '__main__':
    main()
