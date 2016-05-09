#!/usr/bin/env python
# _*_ coding:utf-8 _*_
 
with open('./dns.txt', 'a+') as fo:
    fo.seek(0)
    fo.readline()
    cur = fo.tell() - 2
    fo.seek(cur)
    fo.write('8.8.8.8'+ ' \n')
    fo.seek(0)
    fo.readlines()
