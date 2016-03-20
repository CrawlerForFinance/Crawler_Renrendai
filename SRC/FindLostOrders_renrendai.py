#! /usr/bin/python3.4
# -*- coding: utf-8 -*-

__author__ = 'WangMiaofei'

import os, csv, time


def findLostOrder(path, writer):
    reader = csv.DictReader(open(path, 'r'))
    lineCount = 0
    rawList = []
    try:
        for item in reader:
            lineCount += 1
            rawList.append(int(item['序号']))
    except KeyError as e:
        print('Not a valid csv file.')
    rawList.sort()
    if(len(rawList) < 1): return
    lasti = rawList[0]
    for i in rawList[1:]:
        lasti += 1
        #print(i)
        while(i > lasti):
            writer.write(str(lasti)+'\n')
            lasti += 1
#end def findLostOrder()
#---------------------------------------------

if __name__ == '__main__':
    print('**********************************************************')
    print('*Renrendai Tools for Finding lost orders in csv v20150313*')
    print('**********************************************************'+'\n')
    raw_input = input('Input the name of folder:')
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    writer = open(os.getcwd()+"/"+'LostOrder_'+raw_input+'_'+strtime+'.txt', 'w')
    rootdir = os.getcwd()+'/'+raw_input
    for lists in os.listdir(rootdir):
        path = os.path.join(rootdir, lists)
        print("Read file:"+path)
        findLostOrder(path, writer)

    writer.close()
    print("Finished.")