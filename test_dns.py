#!/usr/bin/env python
# _*_ coding: utf-8 _*_

import httplib
import dns.resolver
import argparse
import socket


def is_ipv4(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

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
                            ip = str(j)
                            if ip not in ip_lst and is_ipv4(ip):
                                print ip,'is a new ip'
                                ip_lst.append(ip)
                    return ip_lst
                else:
                    pass 
                line = fo.readline()
        else:
            ip_lst = []            
            dns_name = dns.resolver.query(qname = domain, source= source_ip)
            for  i in  dns_name.response.answer:
                for j in i.items:
                    ip = str(j)
                    if ip not in ip_lst and is_ipv4(ip):
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


if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', action="store", help="enter your domain")
    parser.add_argument('--source_ip', action='store',help='domain resolv source ip')
    options = parser.parse_args()
    domain = options.domain
    source_ip = options.source_ip
    lst = get_domain_ip(domain, source_ip)
    print(lst)
