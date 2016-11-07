from os.path import abspath, dirname, join
from unittest.mock import patch, Mock

from show_my_ip.show_my_ip import get_nic_info_ifconfig

TESTCASE_FOLDER = dirname(abspath(__file__))


@patch('show_my_ip.show_my_ip.get_ifconfig_output')
def test_ifconfig_darwin(get_ifconfig_output):
    with open(join(TESTCASE_FOLDER, 'ifconfig.mac-os-x')) as f:
        get_ifconfig_output.return_value = f.read()

    res = get_nic_info_ifconfig(show_all=False, cidr=True)
    for name, nic in res.items():
        assert nic.name == name

    assert res['en0'].mac_addr == '2c:f0:ee:1a:50:12'
    assert res['en0'].ip_set == {('192.168.0.100', 24)}

    assert res['lo0'].mac_addr == ''
    assert res['lo0'].ip_set == {('127.0.0.1', 8)}


@patch('show_my_ip.show_my_ip.get_ifconfig_output')
def test_ifconfig_archlinux(get_ifconfig_output):
    with open(join(TESTCASE_FOLDER, 'ifconfig.archlinux')) as f:
        get_ifconfig_output.return_value = f.read()

    res = get_nic_info_ifconfig(show_all=False, cidr=True)
    for name, nic in res.items():
        assert nic.name == name

    assert res['enp3s0'].mac_addr == '00:e0:81:d0:ef:57'
    assert res['enp3s0'].ip_set == {('192.168.1.1', 24)}

    assert res['lo'].mac_addr == ''
    assert res['lo'].ip_set == {('127.0.0.1', 8)}


@patch('show_my_ip.show_my_ip.get_ifconfig_output')
def test_ifconfig_freebsd(get_ifconfig_output):
    with open(join(TESTCASE_FOLDER, 'ifconfig.freebsd')) as f:
        get_ifconfig_output.return_value = f.read()

    res = get_nic_info_ifconfig(show_all=False, cidr=True)
    for name, nic in res.items():
        assert nic.name == name

    assert res['re0'].mac_addr == 'e0:3f:49:e7:82:7d'
    assert res['re0'].ip_set == {('192.168.1.1', 25)}

    assert res['lo0'].mac_addr == ''
    assert res['lo0'].ip_set == set([
        ('127.0.0.1', 8),
        ('192.168.0.1', 24),
        ('192.168.0.2', 32),
        ('192.168.0.3', 32),
        ('192.168.0.4', 32),
        ('192.168.0.5', 32),
        ('192.168.0.6', 32),
        ('192.168.0.7', 32),
        ('192.168.0.8', 32),
        ('192.168.0.9', 32),
        ('192.168.0.10', 32),
    ])


@patch('show_my_ip.show_my_ip.get_ifconfig_output')
def test_ifconfig_mint16(get_ifconfig_output):
    with open(join(TESTCASE_FOLDER, 'ifconfig.mint16')) as f:
        get_ifconfig_output.return_value = f.read()

    res = get_nic_info_ifconfig(show_all=False, cidr=True)
    for name, nic in res.items():
        assert nic.name == name

    assert res['wlan0'].mac_addr == 'ff:ff:ff:ff:ff:ff'
    assert res['wlan0'].ip_set == {('192.168.1.36', 24)}

    assert res['lo'].mac_addr == ''
    assert res['lo'].ip_set == {('127.0.0.1', 8)}
