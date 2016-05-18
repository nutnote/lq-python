#!/usr/bin/env python
# -*- coding:utf-8 -*-
# python version: 2.7.x
# 问题描述: 针对上传和下载域名, 解析域名得到的域名的所有ip, 然后通过不同线路对解析出ip发起特定请求, 测试其可用性. 当不可用时发送短信告警.

import dns.resolver
import argparse
import httplib
import json
import socket
import fileinput
import time


def is_ipv4(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

def write_to_file(file, content, vendor, domain, resolver_ip):
    for line in fileinput.input(file, inplace=1):
        lst = line.strip('\n')
        dic = eval(lst)
        if dic['domain'] == domain and dic['vendor'] == vendor and dic['resolver'] == resolver_ip:
            dic['record'] = content
            dt = json.dumps(dic,ensure_ascii=False)
            line = dt+'\n'
            print line
        else:
            print line

def del_space_line(file):
    result = list()
    with open(file, 'r') as fo:
        for line in fo.readlines():
            line =  line.strip()
            if not len(line):
                continue
            line = line + ' \n'
            result.append(line)
    with open(file, 'w') as fo:
        for lt in result:
            fo.write(lt)

def get_domain_ip(file, domain, vendor, resolver_ip):
    with open(file, 'a+') as fo:
        st = fo.read()
        if st:
            if st.find(domain) > 0: 
                fo.seek(0)
                cont = fo.readlines()
                for line in cont:
                    nw = line.strip('\n')
                    lst = eval(nw)
                    do = lst['domain']
                    ven = lst['vendor']
                    resolver = lst['resolver']
                    if domain == do and vendor == ven and resolver_ip == resolver:
                        ip_lst = lst['record']
                        dns_name = dns.resolver.query(qname = domain, source= resolver_ip)
                        for  i in  dns_name.response.answer:
                            for j in i.items:
                                ip = str(j)
                                if ip not in ip_lst and is_ipv4(str(ip)):
                                    print 'For this domain:', domain , ',',ip,'is a new ip'
                                    ip_lst.append(ip)
                        write_to_file(file, ip_lst, ven, domain, resolver_ip)
                        return ip_lst
                    else:
                       # TODO LIST
                       pass
                    line = fo.readline()
            else:
                dic = {}
                ip_lst = []
                dns_name = dns.resolver.query(qname = domain, source= resolver_ip)
                for  i in  dns_name.response.answer:
                    for j in i.items:
                        j = str(j)
                        if j not in ip_lst and is_ipv4(str(j)):
                            ip_lst.append(j)
                dic['vendor'] = vendor
                dic['resolver'] = resolver_ip
                dic['domain'] = domain
                dic['record'] = ip_lst
                cur = fo.tell()
                fo.seek(cur)
                fo.write(str(dic)+'\n') 
        else:
            for vendor,resolver_ip in dic.iteritems():
                dic = {}
                ip_lst = []
                dns_name = dns.resolver.query(qname = domain, source= resolver_ip)
                for  i in  dns_name.response.answer:
                    for j in i.items:
                        j = str(j)
                        if j not in ip_lst and is_ipv4(str(j)):
                            ip_lst.append(j)
                dic['vendor'] = vendor
                dic['resolver'] = resolver_ip
                dic['domain'] = domain
                dic['record'] = ip_lst
                cur = fo.tell()
                fo.seek(cur)
                fo.write(str(dic)+'\n')

def get_nginx_code(ip, port, meth, url, sip):
    try:
        conn = httplib.HTTPConnection(host =ip, port = port, timeout = 5, source_address = (sip, 0))
        conn.request(meth, url)
        res = conn.getresponse()
        code_number  = res.status
    except:
        code_number = 502
    conn.close()
    return code_number

def send_message(local_ip, server_ip, domain,  file_dns, file_user):
    with open(file_dns, 'r') as dns_info:
        cont = dns_info.readlines()
        for line in cont:
            lst = eval(line.strip('\n'))
            do = lst['domain']
            ven = lst['vendor']
            resolver = lst['resolver']
            ip_list = lst['record']
            if server_ip in ip_list and do == domain:
                with open(file_user, 'r') as user_info:
                    user = json.load(user_info)
                    header = {'Content-type': 'application/json'}
                    for i in user:
                        try:
                            conn = httplib.HTTPConnection('message_ip', port)
                            mess = '发起方: ' + socket.gethostname() + ', 线路: ' + ven + " " + do + ', 目的地: '+  server_ip + ' is unavailable. Please oncall OP...'
                            i['message'] = mess
                            params = json.dumps(i)
                            conn.request('POST', '/api/xxxxxx/yyyyy', params, header)
                            res = conn.getresponse()
                            print mess , i['phone_number'], 'send message status:' ,res.reason
                            conn.close()
                        except:
                            print 'send message error...'


if __name__== '__main__':
    dns_sip = {'电信': 'x.x.x.x','联通': 'y.y.y.y', '移动': 'z.z.z.z'}
#    ngx_url = {'domain1': 'url1', 'domain2': 'url2', 'domain3': 'url3'}
    ngx_url = [{'download_domain': {'method': 'GET', 'url': '/xxx'}}, {'upload_domain': {'method': 'POST', 'url': '/yyy'}}]

    for nx in ngx_url:
        dom = [key for key, _ in nx.iteritems()]
        domain = dom[0]
        for _, url_met in nx.iteritems():
            for key, value in url_met.iteritems():
                if 'url' == key:
                    url = value
                elif 'method' == key:
                    method = value
        for vendor, resolver_ip  in dns_sip.iteritems():
            get_domain_ip('/opt/dns/dns.txt', domain, vendor, resolver_ip)
            del_space_line('/opt/dns/dns.txt')
    
    with open('/opt/dns/dns.txt', 'r') as dns_info: 
        cont = dns_info.readlines()
        for line in cont:
            lst = eval(line.strip('\n'))
            do = lst['domain']
            ven = lst['vendor']
            resolver = lst['resolver']
            all_ip_list = lst['record']
            for ip in all_ip_list:
                sip = dns_sip[ven]
                for nx in ngx_url:
                    dom = [key for key, _ in nx.iteritems()]
                    domain = dom[0]
                    for _, url_met in nx.iteritems():
                        for key, value in url_met.iteritems():
                            if 'url' == key:
                                url = value
                            elif 'method' == key:
                                method = value
                   # if do == domain:
                   #     print 'Local ip:', sip, 'domain: ', domain , method,  url  , 'Server: ' ,ip , get_nginx_code(ip, 80, method, url, sip)
                    if do == domain:
                        if domain == 'nb-gate-io.qiniu.com' and get_nginx_code(ip, 80, method, url, sip) != 200:
                            send_message(sip, ip, domain, '/opt/dns/dns.txt', '/opt/dns/user_info.txt')
                        else:
                            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '服务端IP: ', ip, ' Service is ok.'
                        if domain == 'nb-gate-up.qiniu.com' and get_nginx_code(ip, 80, method, url, sip) != 401:
                            send_message(sip, ip, domain, '/opt/dns/dns.txt', '/opt/dns/user_info.txt')
                        else:
                            print time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), '服务端IP: ', ip, ' Service is ok.'
