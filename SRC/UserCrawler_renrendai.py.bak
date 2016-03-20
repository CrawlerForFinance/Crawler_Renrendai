#! /usr/bin/python2.7
# -*- coding: utf-8 -*-

__author__ = "Wang Miaofei"

import urllib, urllib2, cookielib, httplib, threading
import sys, string, time, os, re, argparse
import csv
from bs4 import BeautifulSoup
import socket
from tools_renrendai import *

#constant
LOST_PAGE_LIMIT = int(30)

#for crawl
urlUser = u'https://www.renrendai.com/account/myInfo.action?userId='
urlLoanList = 'https://www.renrendai.com/account/myInfo!userDetailLoanList.action?userId='
urlFP = u'http://www.renrendai.com/financeplan/listPlan!detailPlan.action?financePlanId='
userFolder = 'Users/'

headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.renrendai.com'}

sheetName = [u'用户信息', u'借款列表']
titles = ([u'抓取日期', u'抓取时间', u'用户ID', u'用户昵称', u'注册时间', u'信用等级', u'信用分数', u'持有债权数量', u'持有理财计划数量', u'发布借款数量', u'成功借款数量', u'未还清借款数量', u'逾期次数', u'逾期金额', u'严重逾期笔数'],[u'抓取日期', u'抓取时间', u'用户ID', u'用户昵称', u'借款标题', u'借款ID', u'年利率（%）', u'金额（元）', u'期限（月）', u'是否有逾期记录', u'借款日期', u'借款开始时刻', u'状态'])

#----------------------------------------------
def createWriters(filedirectory, prefix=''):
    createFolder(filedirectory)
    writers = [] #csv writer list
    strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    for i in range(1, len(titles)+1):
        name_sheet = filedirectory+prefix+'_'+strtime+'_'+sheetName[i-1]+'.csv'
        flag_newfile = True
        if os.path.isfile(name_sheet):
            flag_newfile = False
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
        global curID, lostPageCount, exitFlag
        while not exitFlag:
            pageLock.acquire()
            curID += 1
            if(curID > endID):
                exitFlag = True
                break
            curPage = curID
            print('Thread '+str(self.tId)+': downloading User: '+str(curID)+'...')
            req = urllib2.Request(urlUser+str(curID), headers = getRandomHeaders())
            pageLock.release()
            try:
                response = urllib2.urlopen(req)
                m = response.read()
                #print m
                #response.close()
            except (urllib2.URLError) as e:
                if hasattr(e, 'code'):
                    print(str(e.code)+': '+str(e.reason))
                else:
                    print(e.reason)
                continue
            except socket.error as e:
                print('ERROR] Socket error: '+str(e.errno))
                continue
            #end try&except
            if getUserData(m, curPage, writers):
                lostPageCount = 0
            else:
                print('User '+str(curPage)+' is LOST!')
                lostPageCount += 1
                if(lostPageCount > LOST_PAGE_LIMIT):
                    exitFlag = True
                    print('You have got the latest userID!')
            time.sleep(2)
        #end while
#end class DataFetcher
#-------------------------------------------------------
def getUserData(webcontent, userID, writers):
    soup = BeautifulSoup(webcontent)
    if soup.find('img', {'src':'/exceptions/network-busy/img/500.png'}):
        return False #页面丢失
        
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    #个人信息
    nickName = soup.find('span', {'id':'nick-name'}).string
    if nickName == None:
        return True
    tag_credit = soup.find('span', class_='ui-creditlevel')
    if tag_credit:
        creditLevel = tag_credit.get_text()
        creditScore = re.search('\d+', tag_credit['title']).group(0)
    else:
        creditLevel = ''
        creditScore = ''
    #print nickName
    tag_registerDate = soup.find('div', class_='avatar-info')
    if tag_registerDate:
        registerDate = re.search('\d+-\d+-\d+', tag_registerDate.find('p').string).group(0)
    
    #理财统计
    ownInfo = soup.find('div', class_='avatar-invest')
    tag_ownBondsCount = ownInfo.dl.find('dd')
    ownBondsCount = tag_ownBondsCount.find('em').string
    tag_ownFinancePlansCount = tag_ownBondsCount.find_next('dd')
    ownFinancePlansCount = tag_ownFinancePlansCount.find('em').string
    
    buffer_user = [currentDate, currentClock, userID, nickName, registerDate, creditLevel, creditScore, ownBondsCount, ownFinancePlansCount]
    
    #借款统计
    bb = []
    borrowInfo = soup.find('div', class_='avatar-borrow')
    tag_overDueCount = borrowInfo.dl.find('dd')
    overDueCount = tag_overDueCount.find('em').get_text()
    bb.append(overDueCount)
    tag_last = tag_overDueCount
    for i in xrange(5):
        tag_next = tag_last.find_next('dd')
        bb.append(tag_next.find('em').get_text())
    buffer_user.extend([bb[1],bb[0], bb[3], bb[2], bb[5], bb[4]])
    #print buffer_user
    
    writers[0].writerow(buffer_user)
    
    ###借款列表
    pageIndex = 1
    for pageIndex in xrange(1, int(bb[3])/20+2):
        tryCount = 0;
        while(tryCount < 5):
            tryCount += 1
            loanListString = readFromUrl(urlLoanList+str(userID)+'&pageIndex='+str(pageIndex))
            if(loanListString != "null"):break
        #end while
        if(loanListString == "null"):
            print(str(userID)+" User detail loan list Error!")
            return
        loanListRecords = json.loads(loanListString)
        list_userLoan = loanListRecords['data']['loanList']
        #print list_lenderInfo
        for item in list_userLoan:
            buffer_loan = []
            #[u'抓取日期', u'抓取时间', u'用户ID', u'用户昵称', u'借款标题', u'借款ID', u'年利率（%）', u'金额（元）', u'期限（月）', u'是否有逾期记录', u'借款时间', u'状态']
            statusType = item['status']
            status = ''
            if statusType == 'IN_PROGRESS':
                status = '还款中'
            elif statusType == 'FIRST_READY':
                status = '已满标'
            elif statusType == 'FIRST_APPLY':
                status = '申请中'
            elif statusType == 'FAILED':
                status = '已流标'
            elif statusType == 'BAD_DEBT':
                status = '已垫付'
            elif statusType == 'CLOSED':
                status = '已还清'
            else:
                status = statusType
            
            overDuedType = item['overDued']
            if overDuedType == 'TRUE':
                overDue = '1'
            else:
                overDue = '0'
            
            m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['openTime'])
            openDate = m.group(1)
            openClock = m.group(2)
            buffer_loan.extend([currentDate, currentClock, userID, nickName])
            buffer_loan.extend([item['title'], item['loanId'], item['interest'], item['amount'], item['months'], overDue, openDate, openClock, status])
            
            writers[1].writerow(buffer_loan)
        #end for item
    #end for pageIndex
    return True        
#end getUserData()
#------------------------------------------------
def getData(begin_phase, end_phase, filedirectory):
    
    starttime = time.clock()
    lostPageCount = 0 #记录连续404的页面个数
    #lastpage = begin_page #记录抓取的最后一个有效页面
    
    writers = createWriters(filedirectory+fpFolder, 'FP_'+str(begin_phase)+'-'+str(end_phase))

    for i in range(begin_phase, end_phase+1):
        print('Getting No.'+str(i)+' Financial Plan...')
        req = urllib2.Request(urlFP+str(i), headers = getRandomHeaders())
        try:
            response = urllib2.urlopen(req)
            m = response.read()
            #print(m)
            #lastpage = i
            #response.close()
        except (urllib2.URLError) as e:
            if hasattr(e, 'code'):
                print(str(e.code)+': '+str(e.reason))
            else:
                print(e.reason)
            #i = lastpage
            continue
        except socket.error as e:
            print('ERROR] Socket error: '+str(e.errno))
            #i = lastpage 
            continue
        #end try&except
        
        if analyzeFPData(m, i, writers):
            lostPageCount = 0
        else:
            print('[ERROR] Financial plan No.'+str(i)+' has not established!')
            break
    #end for
    
    endtime = time.clock()
    print(u'[execute time]:'+str(endtime-starttime)+'s')
    return
#end def getData()
        
#----------------------------------------
def getInput():
    global startID, endID
    while True:
        try:
            raw_startID = raw_input('Input start User ID:')
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
            raw_endID = raw_input('Input last User ID:')
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
curID = startID
threadCount = 1 #并发线程数
exitFlag = False
lostPageCount = 0
#----------------------------
#main
if __name__=='__main__':
    reload(sys)
    sys.setdefaultencoding('utf-8') #系统输出编码置为utf8

    #reset timeout
    timeout = 100
    socket.setdefaulttimeout(timeout)

    httplib.HTTPConnection._http_vsn = 10
    httplib.HTTPConnection._http_vsn_str = 'HTTP/1.0'


    print '***************************************'
    print '* Renrendai User Spider v0903 *'
    print '***************************************'
    
    config = getConfig()
    filedirectory = config[0]
    threadCount = config[1]
    
    parser = argparse.ArgumentParser(conflict_handler='resolve')
    parser.add_argument('-s', '--start', action='store', dest='startid', help='Set start user ID')
    parser.add_argument('-e', '--end', action='store', dest='endid', help='Set last user ID')
    parser.add_argument('-t', '--threadcount', action='store', dest='threadCount', help='Set thread number', default=threadCount)
    args = parser.parse_args()
    
    if(args.startid != None and args.endid != None):
        startID = int(args.startid)
        endID = int(args.endid)
    else:
        getInput()
    threadCount = int(args.threadCount)
    
    if login():
        print '------------INPUT INFORMATION---------------------'
        print '- StartID = '+str(startID)
        print '- EndID   = '+str(endID)
        print '------------INPUT INFORMATION---------------------'
        
        startTime = time.clock()
        curID = startID-1
        pageLock = threading.Lock()
        threads = []
        writers = createWriters(filedirectory+userFolder, 'user_'+str(startID)+'-'+str(endID))
        
        for i in xrange(threadCount):
            thread = DataFetcher(i+1, writers)
            threads.append(thread)
        for t in threads:
            t.start()
            
        while(curID <= endID):
            pass
        exitFlag = True
        
        for t in threads:
            t.join()
        print("Exiting Main Thread")
        endTime = time.clock()
        print('[Total user number]:'+str(curID-startID))
        print('[Total execute time]:'+str(endTime-startTime)+'s')
        #getData(startID, endID, filedirectory)
