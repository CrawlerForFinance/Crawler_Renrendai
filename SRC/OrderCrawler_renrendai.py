#! /usr/bin/python3.4
# -*- coding: utf-8 -*-
from msilib.schema import File

__author__ = "Wang Miaofei"

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, http.cookiejar, http.client, threading
import sys, string, time, os, re, argparse
import csv
import textwrap
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *
import importlib

#constant
LOST_PAGE_LIMIT = int(20)

#for crawl
urlLoan = 'http://www.we.com/lend/detailPage.action?loanId='
#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36 Firefox/4.0b13pre', 'Host':'www.we.com'}

sheetName = ['1标的详情', '2投标记录', '3还款表现', '4债权信息', '5转让记录', '6发标人信息', '7留言板', '8催收跟进']
titles = (['抓取时间', '序号', '类型', '认证或担保机构', '标题', '总额（元）', '利率(%)', '还款期限（月）', '开放时间(openTime)', '开始投标时间(beginBidTime)', '满标时间(readyTime)', 'passTime', 'startTime', '还款结束时间(closeTime)', '状态', '垫付金额','垫付时间','剩余期数','保障方式', '提前还款率(%)', '还款方式', '月还本息', '投标进度(%)', '满标用时', '用户ID', '用户名', '年龄', '学历', '婚姻', '公司行业', '公司规模', '岗位职责', '工作城市', '工作时间', '收入范围', '房产', '房贷', '车产', '车贷', '工作类型', '信用等级','信用评分', '申请借款（笔）', '成功还款（笔）', '还清笔数（笔）', '信用额度', '借款总额', '待还本息（元）', '逾期金额（元）', '逾期次数（次）', '严重逾期', '信用报告', '信用报告通过日期', '身份认证', '身份认证通过日期', '工作认证', '工作认证通过日期', '收入认证', '收入认证通过日期', '房产认证', '房产认证通过日期', '购车认证', '购车认证通过日期', '结婚认证', '结婚认证通过日期', '学历认证', '学历认证通过日期', '技术职称认证', '技术职称认证通过日期', '手机认证', '手机认证通过日期', '微博认证', '微博认证通过日期', '居住地证明', '居住地证明通过日期', '视频认证', '视频认证通过日期', '借款描述'], ['抓取时间','序号', '投标人ID', '投标人昵称', '是否手机投标', '投标金额', '投标时间', '投标方式','理财期数'], ['抓取时间', '序号', '合约还款日期', '状态', '应还本息', '应付罚息', '实际还款日期'], ['抓取时间', '序号', '债权人ID', '债权人昵称', '待收本金（元）', '持有份数（份）', '投标方式', '理财期数'], ['抓取时间', '序号', '债权买入者昵称', '债权买入者ID','债权买入者理财计划期数', '债权卖出者昵称', '债权卖出者ID', '债权卖出者理财计划期数', '交易金额', '交易份数', '交易时间'], ['抓取时间', '发标人ID', '发标人昵称', '注册时间', '持有债权数量（笔）', '持有理财计划数量（笔）', '发布借款数量', '成功借款数量（笔）', '未还清借款数量', '逾期次数', '逾期金额', '严重逾期笔数'], ['抓取时间', '序号', '留言者ID', '留言者昵称', '留言日期', '留言时间', '留言内容'], ['抓取时间', '序号', '催收时间', '联系人', '描述'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(titles)+1):
        name_sheet = filedirectory+'rrdai_'+sheetName[i-1]+'_'+prefix+'_'+strtime+'.csv'
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
        if PY3:
            file_sheet = open(name_sheet, 'w', newline='')
        else:
            file_sheet = open(name_sheet, 'wb')
            file_sheet.write('\xEF\xBB\xBF')

        writer = csv.writer(file_sheet)
        writers.append(writer)
        if flag_newfile:
            writer.writerow(titles[i-1])
    return writers
#------------------------------------------------
class DataFetcher(threading.Thread):
    def __init__(self, tId, writers):
        threading.Thread.__init__(self)
        self.tId = tId
        self.writers = writers
    def run(self):
        global orderNo, exitFlag, lostPageCount
        while not exitFlag:
            orderLock.acquire()
            if(orderNo > orderLen):
                exitFlag = True
                break
            try:
                curOrder = (int)(orderList[orderNo-1])
            except: #order序号解析错误
                print(("   [ERROR] Line "+str(orderNo)+': '+orderList[orderNo-1].strip()+' is not a valid number!'))
                orderNo += 1
                lostPageCount += 1
                orderLock.release()
                continue
            print(('Thread '+str(self.tId)+': downloading Loan: '+str(curOrder)))
            #orderNo += 1
            #orderLock.release()
            req = urllib.request.Request(urlLoan+str(curOrder),headers = getRandomHeaders()) 
            
            try:
                response = urllib.request.urlopen(req)
                
                m = response.read()
                #response.close()
            except (urllib.error.URLError) as e:
                if hasattr(e, 'code'):
                    print('   [ERROR] URL error in urlopen().'+(str(e.code)+': '+str(e.reason)))
                else:
                    print((e.reason))
                time.sleep(5)
                continue
            except socket.error as e:
                print('   [ERROR] Socket error in urlopen().')
                time.sleep(5)
                continue
            except Exception as e:
                print('   [ERROR] Some error in urlopen().')
                print(traceback.format_exc())
                time.sleep(5)
                continue
            else:
                orderNo += 1
            finally:
                orderLock.release()
            #end try&except

            try:
                flag = analyzeData(m, writers)
                if flag:
                    lostPageCount = 0;
                else:
                    lostPageCount += 1
                    print(('   [ERROR] Loan '+str(curOrder)+' is LOST!'))
            except Exception as e:
                print("   [ERROR] Some error in analyzeData()")
                print(traceback.format_exc())
                print(('Loan '+str(curOrder)+' is LOST!'))

            time.sleep(randint(1, 7))
        #end while
#end class DataFetcher
#----------------------------------------
def getInput():
    global startID, endID
    while True:
        try:
            raw_startID = input('Input start order ID:')
            startID = int(raw_startID)
            if startID < 1:
                print('Start ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_startID == ''):
                startID = 1
                break
            print('Not a number! Please input again!')
            continue
    while True:
        try:
            raw_endID = input('Input end order ID:')
            endID = int(raw_endID)
            if endID < 1:
                print('End ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_endID == ''):
                endID = startID+3000
                break
            print('Not a number! Please input again!')
            continue
#----------------------------
#global variable
threadCount = 1 #并发线程数
exitFlag = False
lostPageCount = 0
sleepTime = 2
orderFilename = 'orderlist'
orderList = []
orderNo = 1
orderLen = 0
PY3 = True
#----------------------------
#main
if __name__=='__main__':

    #sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    #reset timeout
    timeout = 100
    socket.setdefaulttimeout(timeout)

    #http.client.HTTPConnection._http_vsn = 10
    #http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'
    
    print('*********************************************************')
    print('* Renrendai Loan Spider for Individual Orders v20150326 *')
    print('*********************************************************')
    config = getConfig()
    filedirectory = config[0]
    threadnumber = config[1]

    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-t', '--threadcount', action='store', dest='threadCount', help='Set thread number', default=threadnumber)
    args = parser.parse_args()

    threadCount = int(args.threadCount)
    
    try:
        orderFile = open(os.getcwd()+'/'+orderFilename, 'r')
        orderList = orderFile.readlines()
        orderLen = len(orderList)
        #print proxyList
    except:
        print('No orderList file!')

    if login():
        print(("\nTotal line number: "+str(orderLen)+"."))
        startTime = time.clock()
        orderLock = threading.Lock()
        threads = []
        #writers = createWriters(filedirectory, 'order')   
        writers = []
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
        filenames = []
        prefix = 'order'
        for i in range(1, len(titles)+1):
            name_sheet = filedirectory+'rrdai_'+sheetName[i-1]+'_'+prefix+'_'+strtime+'.csv'
            filenames.append(name_sheet)

        with openFiles(filenames, 'a', newline='') as files:
            i = 0
            for f in files:
                writer = csv.writer(f, dialect='excel')
                
                writers.append(writer)
                writer.writerow(titles[i])
                i += 1
            for i in range(threadCount):
                thread = DataFetcher(i+1, writers)
                threads.append(thread)
            try:
                for t in threads:
                    t.start()
                while(orderNo <= orderLen):
                    for f in files: f.flush()
                    pass
                exitFlag = True
            except KeyboardInterrupt:
                print("Keyboard Interrupt! Program stop!")
                exitFlag = True
            else:
                for t in threads: t.join()

            orderFile.close()


        print('Exiting Main Thread')
        endTime = time.clock()
        print(('[Valid order number]:'+str(orderLen-lostPageCount)))
        print(('[Total execute time]:'+str(endTime-startTime)+'s'))
        #os.system('pause')
#end main