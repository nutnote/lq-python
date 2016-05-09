#!/usr/bin/env python
#-*- coding:utf-8 -*-

import dns.resolver
import argparse
import httplib
import json
import socket
import fileinput


# 判断是否为有效的ip
def is_ipv4(ip):
    try:
        socket.inet_aton(ip)
        return True
    except:
        return False

# 当等于给定的域名时, 将指定内容写入特定文件中
def write_to_file(file, content, domain):
    for line in fileinput.input(file, inplace=1):
        st = str(line)
        st = st.strip()
        lst = st.split(' ')
        if lst[0] == domain:
            print line.rstrip(' \n'),content
        else:
            print line

# 删除指定文件的空行
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

# dns解析, 结果为以列表形式返回该域名解析到的所有A记录的ip
# dns.txt 文件初始为空, 或添加需解析的ip，并以空格结尾。
# dns.txt 文件内容为: 域名开头, 后跟域名解析出的所有ip, 最后以空格结尾. 格式如下: 
# '''domain x.x.x.x y.y.y.y ''' 
def get_domain_ip(domain, source_ip):
    with open('/opt/dns/dns.txt', 'a+') as fo:
        st = fo.read()
        if st:
            fo.seek(0)
            cont = fo.readlines()
            for line in cont:
                lst = list(line.split(' '))
                do = lst[0]
                if domain == do:
                    ip_lst = lst[1:-1]
                    dns_name = dns.resolver.query(qname = domain, source= source_ip)
                    for  i in  dns_name.response.answer:
                        for j in i.items:
                            ip = str(j)
                            if ip not in ip_lst and is_ipv4(str(ip)):
                                print 'For this domain:', domain , ',',ip,'is a new ip'
                                ip_lst.append(ip)
                                write_to_file('/opt/dns/dns.txt', ip, domain)
                    return ip_lst
                else:
                    pass
                line = fo.readline()
        else:
            ip_lst = []
            dns_name = dns.resolver.query(qname = domain, source= source_ip)
            for  i in  dns_name.response.answer:
                for j in i.items:
                    j = str(j)
                    if j not in ip_lst and is_ipv4(str(j)):
                        ip_lst.append(j)
            cur = fo.tell()
            fo.seek(cur)
            fo.write(domain+' ')
            for ip in ip_lst:
                fo.write(str(ip)+' ')
            fo.write('\n')
            return ip_lst

# 从本地的不同运营商向目标服务器的特定ip发起url请求
def get_nginx_code(ip, port, meth, url, sip):
    try:
        conn = httplib.HTTPConnection(host =ip, port = port, timeout = 5, source_address = sip)
        conn.request(meth, url)
        res = conn.getresponse()
        code_number  = res.status
    except:
        code_number = 502
    conn.close()
    return code_number

# 短信接口, 用来发送告警信息
def send_message(local_ip, server_ip):
    with open('/opt/dns/user_info.txt', 'r') as fo:
        lst = json.load(fo) 
        header = {'Content-type': 'application/json'}
        for i in lst:
            try:
                conn = httplib.HTTPConnection('x.x.x.x', post)
                mess = 'Local ip: ' + local_ip + ' connect server ip: '+  server_ip + ' is unavailable.'
                i['message'] = mess 
                params = json.dumps(i)
                conn.request('POST', '/api/', params, header)
                res = conn.getresponse()
                print mess , i['phone_number'], 'send message status:' ,res.reason 
                conn.close()
            except:
                pass



if __name__== '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--domain', action="store", help="enter your domain")
    parser.add_argument('--method', action="store" , help="nginx method")
    options = parser.parse_args()
    domain = options.domain
    method = options.method
   
    # t.t.t.t: 表示为本机电信ip; u.u.u.u: 表示本机联通ip; m.m.m.m: 表示本地移动ip
    dns_sip = ['t.t.t.t', 'u.u.u.u', 'm.m.m.m']
    ngx_sip = [('t.t.t.t', 0), ('u.u.u.u', 0), ('m.m.m.m', 0)]
    lst= []
    for source_ip in dns_sip:
        lst = get_domain_ip(domain, source_ip)
        lst.extend(lst)
    print lst


    del_space_line('/opt/dns/dns.txt')
    for ip in lst:
        if method == 'GET' or method == 'get':
            method = method.upper()
            url = '/1.png'
            for sip in ngx_sip:
                if get_nginx_code(ip, 80, method, url, sip) != 200:
                    send_message(sip[0], ip)
           #     print 'Local ip:', sip[0], method , 'Server: ' ,ip , get_nginx_code(ip, 80, method, url, sip)
        elif method == 'POST' or method == 'post':
            method = method.upper()
            url = '/mkblk/'
            for sip in ngx_sip:
                if get_nginx_code(ip, 80, method, url, sip) != 401:
                    send_message(sip[0], ip)
               # print 'Local ip:', sip[0], method , 'Server: ' ,ip , get_nginx_code(ip, 80, method, url, sip)
        else:
            print("Invalid method")
