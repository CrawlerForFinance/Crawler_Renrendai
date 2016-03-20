# python 3.4
# coding: utf-8
from UserCrawler_renrendai import getData

_author_ = "Li Yanqing"

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, http.cookiejar, http.client
import sys, string, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *
import importlib

#constant
LOST_PAGE_LIMIT = int(20)

'''
#for crawl
urlLoan = 'http://www.renrendai.com/lend/detailPage.action?loanId='
urlUList_json = 'https://www.renrendai.com/financeplan/listPlan!listPlanJson.action?category='
urlUP = 'http://www.renrendai.com/financeplan/listPlan!detailPlan.action?financePlanId='
urlSList_json = 'https://www.renrendai.com/autoinvestplan/listPlan!listPlanJson.action?pageIndex='
urlSP = 'http://www.renrendai.com/autoinvestplan/listPlan!detailPlan.action?autoInvestPlanId='
'''
#for crawl
urlLoan = 'http://www.we.com/lend/detailPage.action?loanId='
urlUList_json = 'https://www.we.com/financeplan/listPlan!listPlanJson.action?category='
urlUP = 'http://www.we.com/financeplan/listPlan!detailPlan.action?financePlanId='
urlSList_json = 'https://www.we.com/autoinvestplan/listPlan!listPlanJson.action?pageIndex='
urlSP = 'http://www.we.com/autoinvestplan/listPlan!detailPlan.action?autoInvestPlanId='

spFolder = 'SalaryPlan/'

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.we.com'}
jsonheaders={'Accept':'application/json, text/javascript, */*; q=0.01', 'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36', 'Host':'www.we.com', 'X-Requested-With':'XMLHttpRequest'}

sheetName = ['1outline', '2plan', '3plan_preorder', '4plan_order']
titles = (['抓取时间', '计划名称', '计划id', '计划金额（元）', '实际加入人次', '预期年化收益', '累计收益（元）', '状态'], ['抓取时间', '计划名称','计划ID', '剩余人数', '预期收益（%/年）', '投标范围', '保障方式', '计划状态', '收益处理方式','理财期限（月）', '已获收益','满额用时', '每月投资日','退出时间', '加入费率', '退出费率', '月投资金额','提前退出', '加入总人次', '加入总金额', '使用时长','自动投标次数', '为用户赚取', '平均利率','帮助借款者人数'], ['计划名称', '计划id', '理财人昵称', '理财人id', '加入金额', '预定时间', '来源', '状态'], ['计划名称', '计划id', '理财人昵称', '理财人ID', '加入金额', '加入时间'], ['抓取时间', '计划名称', '计划id', '发布时间', '计划金额', '自动投标次数', '帮助借款用户', '为用户赚取', '加入人数', '满额用时'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(sheetName)+1):
        #name_sheet = filedirectory+'rrdai_'+sheetName[i-1]+'_'+prefix+'_'+strtime+'.csv'
        #print()
        name_sheet = filedirectory+prefix+'/rrdai_'+sheetName[i-1]+'_'+'_'+strtime+'.csv'
        
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
        if PY3:
            file_sheet = open(name_sheet, 'w', newline='')
            #file_sheet = open(name_sheet, 'w')
        else:
            file_sheet = open(name_sheet, 'wb')
            file_sheet.write('\xEF\xBB\xBF')

        writer = csv.writer(file_sheet)
        writers.append(writer)
        if flag_newfile:
            writer.writerow(titles[i-1])
    return writers#----------------------------------------
#------------------------------------------------
#------------------------------------------------
def getList():
    pageIndex = 1
    #print(X)
    while(True):
        m = readFromUrl(urlSList_json+str(pageIndex), headers = jsonheaders)
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
            if stateCode == '0': state = '"立即加入"'
            elif stateCode == '2': state = '"收益中"' #现有两种状态码，可能需要增加
            elif stateCode:
                state = '"'+stateCode+'"'
            name = item['name'] 
            if name:
                name = '"'+name+'"'
            buffer = [currentTime, name, item['id'], item['amount'], item['subpointCountActual'], item['expectedYearRate'], item['earnInterest'], state]
            writers[0].writerow(buffer)
            
            content = readFromUrl(urlSP+str(item['id']))
            
            analyzeSPData(content, item['id'], writers)
            
            
            
        if(totalPage > pageIndex): pageIndex += 1
        else: break;
        
        time.sleep(randint(3, 7))
#end def getList()
#----------------------------------------------------------
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
    print('*Renrendai Salary Plan Spider v1007*')
    print('***************************************')

    filedirectory = getConfig()[0]
    if login():
        writers = createWriters(filedirectory, 'SP')
        createFolder(filedirectory+'SP')
        getList()
        
        #for w in writers: w.close()
        #getData(startID, endID, filedirectory)
    #os.system('pause')
#end main