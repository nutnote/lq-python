#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import fileinput

file = '''www.baidu.com 115.239.211.112 115.239.210.27 
www.taobao.com 222.73.134.63 101.226.178.178 \n'''


with open('/tmp/test.txt', 'w+') as fo:
    fo.write(file)

for line in fileinput.input('/tmp/test.txt'):
    type(line)
    st = str(line)
    lst = st.split(' ')
    if lst[0] == 'www.baidu.com':
        print line.rstrip(' \n'),fileinput.filename(),fileinput.lineno()
    else:
        
        print line

with open('/tmp/test.txt', 'r') as fo:
    fo.readlines()
