def show_my_ip ():
    import re
    import subprocess as sub
    ipconfig = sub.check_output(['ipconfig'])
    ipconfig = ipconfig.decode('cp950').encode('utf8')
    ipconfig = re.sub(r'\r\n', r'\n', ipconfig)
    ipconfig = re.sub(r'\n\n', r'\n', ipconfig)

    NIC_name_re = '[^ \n].*'
    IP_re = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    other_descript_re = ' +.*:.*\n'

    result = re.findall(
        r'^(?P<NAME>[^ \n].*):\n'+
        r'(?:' + other_descript_re + r')*' +
        r' +.*IPv4.*: *('+IP_re+r')\n'+
        r'(?:' + other_descript_re + r')*',
        ipconfig,
        re.MULTILINE
    )

    return dict(result)

if __name__ == '__main__':
    print 'Detected IP addresses:\n'
    for i,j in show_my_ip().iteritems():
        print i + ':'
        print '   ',j
        print ''
