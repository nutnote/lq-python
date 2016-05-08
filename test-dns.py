#!/usr/bin/env python
# _*_ coding: UTF-8 _*_

import httplib
import dns.resolver
import argparse
import socket


def is_ipv4(ip):
    res = 200
    try:
        socket.inet_aton(ip)
    except:
        res = res - 200
    return res

def get_domain_ip(domain, source_ip):
    with open('/opt/dns/dns.txt', 'a+') as fo:
        st = fo.read()
        if st:
            fo.seek(0)
            line = fo.readline()
            while line:
                lst = list(line.split(' '))
                do = lst[0]
                if domain == do:
                    ip_lst = lst[1:-1]
                    dns_name = dns.resolver.query(qname = domain, source= source_ip)
                    for  i in  dns_name.response.answer:
                        for j in i.items:
                            ip = str(j.address)
                            if ip not in ip_lst:
                                print ip,'is a new ip'
                                ip_lst.append(ip)
                        #        cur = fo.tell()
                        #        fo.seek(cur)
                        #        fo.write(j.address+' \n')
                    return ip_lst
                else:
                    pass 
                line = fo.readline()
        else:
            ip_lst = []            
            dns_name = dns.resolver.query(qname = domain, source= source_ip)
            for  i in  dns_name.response.answer:
                for j in i.items:
                    if j.address not in ip_lst:
                        ip_lst.append(j.address)
            cur = fo.tell()
            fo.seek(cur)
            print(ip_lst)
            fo.write(domain+' ')
            for ip in ip_lst:
                print(ip)
                fo.write(str(ip)+' ')
            fo.write(' ')
            return ip_lst


#def get_nginx_code(ip, port, meth, url):
#    try:
#        conn = httplib.HTTPConnection(ip, port, timeout = 3)
#        conn.request(meth, url)
#        res = conn.getresponse()
#        code_number  = res.status
#    except:
#        code_number = 502
#    conn.close()
#    return code_number


if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', action="store", help="enter your domain")
    parser.add_argument('--source_ip', action='store',help='domain resolv source ip')
    options = parser.parse_args()
    domain = options.domain
    source_ip = options.source_ip
    lst = get_domain_ip(domain, source_ip)
    print(lst)
