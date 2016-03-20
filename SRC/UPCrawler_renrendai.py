#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, http.cookiejar, http.client
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *
import importlib

#constant
LOST_PAGE_LIMIT = int(20)

#for crawl
'''
urlLoan = 'http://www.renrendai.com/lend/detailPage.action?loanId='
urlUList_json = 'https://www.renrendai.com/financeplan/listPlan!listPlanJson.action?category='
urlUP = 'http://www.renrendai.com/financeplan/listPlan!detailPlan.action?financePlanId='
fpFolder = 'FinancePlan/'
'''
#for crawl
urlLoan = 'http://www.we.com/lend/detailPage.action?loanId='
urlUList_json = 'http://www.we.com/financeplan/listPlan!listPlanJson.action?category='
urlUP = 'http://www.we.com/financeplan/listPlan!detailPlan.action?financePlanId='
fpFolder = 'FinancePlan/'

#filedirectory = u'D:\datas\pythondatas\renrendai\\'
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.we.com'}
jsonheaders={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.we.com', 'X-Requested-With':'XMLHttpRequest'}

sheetName = ['1outline', '2plan', '3plan_preorder', '4plan_order']
titles = (['抓取时间', '计划名称', '计划id', '计划金额（元）', '加入人次', '预期年化收益', '累计收益（元）', '状态'], ['抓取时间', '计划名称','计划ID', '计划金额', '预期收益（%/年）', '投标范围','收益处理方式','已获收益', '满额用时','保障方式', '计划状态', '锁定期限（月）', '加入条件（元）', '加入上限（元）', '开放加入时间', '进入锁定时间', '退出时间', '加入费率', '退出费率', '提前退出费率', '预定人次', '未支付金额', '加入总人次', '加入总金额','使用时长', '自动投标次数', '为用户赚取', '平均利率','帮助借款者人数'], ['计划名称', '计划id', '理财人昵称', '理财人id', '加入金额', '预定时间', '来源', '状态'], ['计划名称', '计划id', '理财人昵称', '理财人ID', '加入金额', '加入时间'], ['抓取时间', '计划名称', '计划id', '发布时间', '计划金额', '自动投标次数', '帮助借款用户', '为用户赚取', '加入人数', '满额用时'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(sheetName)+1):
        name_sheet = filedirectory+prefix+'/rrdai_'+sheetName[i-1]+'_'+'_'+strtime+'.csv'
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
def getList():
    for X in ['A', 'B', 'C']:
        print(('抓取U计划'+X+'...'))
        
        pageIndex = 1
        #print(X)
        while(True):
            m = readFromUrl(urlUList_json+X+'&pageIndex='+str(pageIndex), headers = jsonheaders)
            #print m
            scriptData = json.loads(m)
            totalPage = scriptData['data']['totalPage']
            
            ulist = scriptData['data']['plans']
            
            
            for item in ulist:
                buffer = []
                currentDate = getTime('%Y-%m-%d')
                currentClock = getTime('%H:%M:%S')
                currentTime = getTime('%Y/%m/%d %H:%M:%S')
                stateCode = item['status']
                state = stateCode
                if stateCode == '6': state = '"收益中"'
                elif stateCode == '2': state = '"预定满额"'
                elif stateCode == '7': state = '"开放期"'
                elif stateCode == '0': state = '"等待预定"'
                elif stateCode == '5': state = '"计划满额"'
                elif stateCode == '8': state = '"收益中"' #奇怪的问题，U计划id 76
                
                name = item['name']
                if name:
                    name = '"'+ name+'"'
                buffer = [currentTime, name, item['id'], item['amount'], item['subPointCount'], item['expectedYearRate'], item['earnInterest'], state]
                writers[0].writerow(buffer)
                
                content = readFromUrl(urlUP+str(item['id']))
                analyzeUPData(content, item['id'], writers)
                
            
            if(totalPage > pageIndex): pageIndex += 1
            else: break;
            
            time.sleep(randint(3, 7))
#end def getList()
#------------------------------------------------
def getData(begin_phase, end_phase, filedirectory):
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    writers = createWriters(filedirectory+fpFolder, 'FP_'+str(begin_phase)+'-'+str(end_phase))

    for i in range(begin_phase, end_phase+1):
        print(('Getting No.'+str(i)+' Financial Plan...'))
        req = urllib.request.Request(urlUP+str(i), headers = getRandomHeaders())
        try:
            response = urllib.request.urlopen(req)
            m = response.read()
            #print(m)
            #lastpage = i
            #response.close()
        except (urllib.error.URLError) as e:
            if hasattr(e, 'code'):
                print((str(e.code)+': '+str(e.reason)))
            else:
                print((e.reason))
            #i = lastpage
            continue
        except socket.error as e:
            print(('ERROR] Socket error: '+str(e.errno)))
            #i = lastpage 
            continue
        #end try&except
        
        if analyzeUPData(m, i, writers):
            lostPageCount = 0
        else:
            print(('[ERROR] Financial plan No.'+str(i)+' has not established!'))
            break
    #end for
    
    endtime = time.clock()
    print(('[execute time]:'+str(endtime-starttime)+'s'))
    return
#end def getData()
        
#----------------------------------------
def getInput():
    global startID, endID
    while True:
        try:
            raw_startID = input('Input start Financial Plan ID:')
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
            raw_endID = input('Input last  Financial Plan ID:')
            endID = int(raw_endID)
            if endID < 1:
                print('Last ID illegal! Please input again!')
                continue
            break
        except:
            if(raw_endID == ''):
                endID = 1000
                break
            print('Not a number! Please input again!')
            continue    
#----------------------------
#global variable
startID = 1
endID = 1000
writers = []
PY3 = True
#----------------------------
#main
if __name__ == '__main__':
    if sys.version > '3':
        PY3 = True
    else:
        PY3 = False
    importlib.reload(sys)
    #sys.setdefaultencoding('utf-8') #系统输出编码置为utf8
    timeout = 100
    socket.setdefaulttimeout(timeout)
    #http.client.HTTPConnection._http_vsn = 10
    #http.client.HTTPConnection._http_vsn_str = 'HTTP/1.0'

    print('***************************************')
    print('*Renrendai U Finance Plan Spider v0307*')
    print('***************************************')

    filedirectory = getConfig()[0]
    if login():
        writers = createWriters(filedirectory, 'UP')
        
        getList()

        #for w in writers: w.close()
        #getData(startID, endID, filedirectory)
    #os.system('pause')
#end main
