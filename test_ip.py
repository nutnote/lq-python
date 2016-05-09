#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import socket
import dns.resolver

domain = 'www.baidu.com'

def is_ipv4(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

dns_num = dns.resolver.query(domain)
for i in dns_num.response.answer:
    for i in i.items:
        print(i)
        print(is_ipv4(i))
