#!/usr/bin/env python
# _*_ coding:utf-8 _*_

import fileinput

file = '''www.baidu.com  115.239.211.112 115.239.210.27  
www.taobao.com 222.73.134.63 101.226.178.178 '''


with open('./test.txt', 'w+') as fo:
    fo.write(file)

for line in fileinput.input('./test.txt',inplace=1):
    print line.rstrip(' \n'),fileinput.filename(),fileinput.lineno()

with open('./test.txt', 'r') as fo:
    fo.readlines()
