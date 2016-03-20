#! /usr/bin/python3.4
# -*- coding: utf-8 -*-
from pydoc import describe

__author__ = "Wang Miaofei"

import urllib.request, urllib.parse, urllib.error, urllib.request, urllib.error, urllib.parse, http.cookiejar
import sys, string, traceback, time, os, re, json
import csv
from bs4 import BeautifulSoup
import socket, ssl
from random import randint
import configparser
from contextlib import contextmanager

#config
configfileName = 'config.ini'
filedirectory = 'D:/datas/pythondatas/renrendai/'
username = '15120000823'
password = 'wmf123456'
threadnumber = '2'
proxy_enable = 0
proxy_host = ''
proxy_port = ''

'''
#For login
urlLogin = 'https://www.renrendai.com/j_spring_security_check'
urlIndex = 'http://www.renrendai.com/'
urlLenderRecordsPrefix = 'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderRecords&loanId='
urlRepayDetailPrefix = 'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=repayDetail&loanId='
urlLenderInfoPrefix = 'http://www.renrendai.com/lend/getborrowerandlenderinfo.action?id=lenderInfo&loanId='
urlTransferLogPrefix = 'http://www.renrendai.com/transfer/transactionList.action?loanId='
urlUserPrefix = 'https://www.renrendai.com/account/myInfo.action?userId='
urlCommentPrefix = 'http://www.renrendai.com/lend/loanCommentList.action?loanId='
urlCollectionPrefix = 'http://www.renrendai.com/lend/dunDetail.action?loanId='

#for Financial Plan
urlFPLenderPrefix = 'http://www.renrendai.com/financeplan/getFinancePlanLenders.action?financePlanStr='
urlFPPerformancePrefix = 'http://www.renrendai.com/financeplan/listPlan!planResults.action?financePlanId='
urlFPReservePrefix = 'http://www.renrendai.com/financeplan/getFinancePlanLenders!reserveRecord.action?financePlanStr='

#for salary plan AutoinvestPlan
urlSPBuyerPrefix = 'http://www.renrendai.com/autoinvestplan/listPlan!getAutoInvestPlanBuyerRecords.action?autoInvestPlanId='
urlSPPerformancePrefix = 'http://www.renrendai.com/autoinvestplan/listPlan!planResults.action?autoInvestPlanId='
'''
#For login
urlLogin = 'https://www.we.com/j_spring_security_check'
urlIndex = 'http://www.we.com/'
urlLenderRecordsPrefix = 'http://www.we.com/lend/getborrowerandlenderinfo.action?id=lenderRecords&loanId='
urlRepayDetailPrefix = 'http://www.we.com/lend/getborrowerandlenderinfo.action?id=repayDetail&loanId='
urlLenderInfoPrefix = 'http://www.we.com/lend/getborrowerandlenderinfo.action?id=lenderInfo&loanId='
urlTransferLogPrefix = 'http://www.we.com/transfer/transactionList.action?loanId='
urlUserPrefix = 'https://www.we.com/account/myInfo.action?userId='
urlCommentPrefix = 'http://www.we.com/lend/loanCommentList.action?loanId='
urlCollectionPrefix = 'http://www.we.com/lend/dunDetail.action?loanId='

#for Financial Plan
urlFPLenderPrefix = 'http://www.we.com/financeplan/getFinancePlanLenders.action?financePlanStr='
urlFPPerformancePrefix = 'http://www.we.com/financeplan/listPlan!planResults.action?financePlanId='
urlFPReservePrefix = 'http://www.we.com/financeplan/getFinancePlanLenders!reserveRecord.action?financePlanStr='

#for salary plan AutoinvestPlan
urlSPBuyerPrefix = 'http://www.we.com/autoinvestplan/listPlan!getAutoInvestPlanBuyerRecords.action?autoInvestPlanId='
urlSPPerformancePrefix = 'http://www.we.com/autoinvestplan/listPlan!planResults.action?autoInvestPlanId='

ipAddress = ['191.124.5.2', '178.98.24.45,231.67.9.28'] 
host = 'www.we.com'
userAgent = ['Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/34.0.1847.116 Chrome/34.0.1847.116 Safari/537.36', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:29.0) Gecko/20100101 Firefox/29.0', 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36']
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.117 Safari/537.36', 'Host':'www.we.com'}

#代理相关
proxyfileName = 'proxylist'
proxyList = []

TRY_LOGIN_TIMES = 5 
#--------------------------------------------------
def getConfig(configPath = None):
    global username, password, proxy_enable, proxy_host, proxy_port
    if(configPath == None):
        configPath = configfileName
    cf = configparser.ConfigParser()
    cf.read(configPath)
    
    filedirectory = cf.get('base', 'filedirectory')+'/'
    username = cf.get('base', 'username')
    password = cf.get('base', 'password')
    threadnumber = cf.get('base', 'threadnumber')
    
    proxy_enable = cf.get('proxy', 'enable')
    proxy_host = cf.get('proxy', 'host')
    proxy_port = cf.get('proxy', 'port')
    
    print('[CONFIG]')
    print(('filedirectory = '+filedirectory))
    print(('username = '+username))
    print(('password = '+password))
    print(('threadnumber = '+str(threadnumber)+'\n'))
    #print(proxy_host)
    #print(proxy_port)
    
    return [filedirectory, threadnumber]
#end def getConfig

#--------------------------------------------------
@contextmanager
def multi_file_manager(files, mode='w+', newline=''):
    files = [open(file, mode, newline=newline) for file in files]
    yield files
    for file in files:
        file.flush()
        file.close()
#--------------------------------------------------
class openFiles():
    def __init__(self, files, mode='w+', newline=''):
        if(isinstance(files, str)):
            files = [files]

        #assert(len(files) == len(modes) and len(files) == len(newlines))
        self.files = files
        self.mode = mode
        self.newline = newline

    def __enter__(self):
        self.fhs = []
        for f in self.files:
            self.fhs.append(open(f, mode=self.mode, newline=self.newline))
        return self.fhs

    def __exit__(self, type, value, traceback):
        for f in self.fhs:
            f.close()

#------------------------------------------------
'''
class writer:
    def writerow(self, row):
        for item in row:
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
        #row = [s.encode('gbk', 'ignore').decode('gbk') for s in row]
        self.writer.writerow(row)
'''
#--------------------------------------------------
#读取配置文件，返回目标文件夹地址
def old_getConfig():
    global username, password
    filedirectory = ""
    threadnumber = 1
    try:
        configfile = open(os.getcwd()+'/'+configfileName, 'r')
        #line = configfile.readline()
        pattern = re.compile('\s*(\w+)\s*=\s*(\S+)\s*')
        for line in configfile:
            #print line
            m = pattern.match(line)
            if m:
                if m.group(1) == 'filedirectory':
                    filedirectory =  m.group(2)+'/'
                elif m.group(1) == 'username':
                    username = m.group(2)
                elif m.group(1) == 'password':
                    password = m.group(2)
                elif m.group(1) == 'threadnumber':
                    threadnumber = m.group(2)
                #print filedirectory
        configfile.close()
    except:
        configfile = open(os.getcwd()+'/'+configfileName, 'wb')
        configfile.write('filedirectory = '+filedirectory+'\n')
        configfile.write('username = '+username+'\n')
        configfile.write('password = '+password+'\n')
        configfile.write('threadnumber = '+str(threadnumber)+'\n')
        configfile.close()
        print('Create new config file!')
    
    createFolder(filedirectory)
    
    print('[CONFIG]')
    print(('filedirectory = '+filedirectory))
    print(('username = '+username))
    print(('password = '+password+'\n'))
    #print('threadnumber = '+str(threadnumber))
    
    return [filedirectory, threadnumber]
#end def getConfig()
#--------------------------------------------------
#获取代理信息
def getProxyList(proxy = None):
    print('Get proxy...')
    global proxyList
    if proxy == None:
        proxy = proxyfileName
    try:
        proxyfile = open(os.getcwd()+'/'+proxy, 'r')
        proxyList = proxyfile.readlines()
        #print proxyList
    except:
        print('No proxy file!')
    return proxyList
#end def getProxyList    
#--------------------------------------------------
#登录函数
def login():
    print('Logging...')
    cj = http.cookiejar.CookieJar()
    if(proxy_enable == '0'):
        print("No proxy.")
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    else:
        #getProxyList()
        print(("Current proxy: "+str(proxy_host)+':'+str(proxy_port)))
        proxy_handler = urllib.request.ProxyHandler({"http": str(proxy_host)+':'+str(proxy_port)})
        #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj), proxy_handler)
    #end ifelse
    urllib.request.install_opener(opener)

    data = {'j_username':username, 'j_password':password, 'rememberme':'on', 'targetUrl':'http://www.renrendai.com', 'returnUrl':'', "Content-Type":" application/x-www-form-urlencoded;charset=utf-8"}
    postdata = urllib.parse.urlencode(data)
    #print("data:"+str(data))
    #print("postdata:"+str(postdata))
    for i in range(TRY_LOGIN_TIMES):
        try:
            req = urllib.request.Request(urlLogin, data=postdata.encode('utf8'), headers=headers)
            #req = urllib.request.Request(urlLogin, data=postdata)
            response = urllib.request.urlopen(req, timeout=30)
            m = response.read()
            #print(m)
            #print("return url:"+response.geturl())
            '''
            if urlIndex != result.geturl(): #通过返回url判断是否登录成功
                print result.geturl()
                print(u'[FAIL]Wrong USERNAME or PASSWORD. Please try again!')
                return False
            '''
            #print result.read()
            response.close()
            print('LOGIN SUCCESS')
            return True
        except socket.timeout as e:
            print("Socket timeout. Reconnect...")
            continue
        except urllib.error.HTTPError as e:
            print("HTTP error code "+e.code)
        except urllib.error.URLError as e:
            print('URLError timeout. Reconnect...'+e.reason)
            continue
        except http.client.HTTPException as e:
            print("http exception.")
        except:
            import traceback
            print('[FAIL]Login failed. Please try again!'+traceback.format_exc())
    #end for
    return True
#end def login()

#--------------------------------------------------
#查看文件夹是否存在：若不存在，则创建
def createFolder(filedirectory):
    if os.path.isdir(filedirectory):
        pass
    else:
        os.makedirs(filedirectory) #可以创建多级目录
    return
#--------------------------------------------------
#生成一个随机的headers
def getRandomHeaders():
    ipNumber = len(ipAddress)
    agentNumber = len(userAgent)
    headers = {'User-Agent': userAgent[randint(0, agentNumber-1)], 'Host': host, 'X-Forwarded-For': ipAddress[randint(0, ipNumber-1)]}
    return headers

#--------------------------------------------------
def getTime(format = None):
    if format:
        strtime = str(time.strftime(format, time.localtime(time.time())))
    else:
        strtime = str(time.strftime('%Y%m%d%H%M', time.localtime(time.time())))
    return strtime
#--------------------------------------------------
def struct2Datetime(timeStruct, targetFormat):
    return time.strftime(targetFormat, timeStruct)
def str2Datetime(str, originFormat, targetFormat = '%Y/%m/%d %H:%M:%S'):
    timeStruct = time.strptime(str,originFormat)
    return struct2Datetime(timeStruct, targetFormat)
#--------------------------------------------------
def cleanString(str):
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    return str.strip()
#--------------------------------------------------
#从url读取页面内容
def readFromUrl(url, formdata = None, headers = None):
    loopCount = 0
    while True:
        loopCount += 1
        if loopCount > 5:
            break
        try:
            response = responseFromUrl(url, formdata, headers)
            if response:
                m = response.read()
                #response.close()
                if(m == None):
                    continue
                #TODO:need to close response?
                return m.decode('utf8')
            else:
                print('response is None')
                return None
        except ssl.SSLError as e:
            print('[ERROR]ssl error in readFromUrl()!')
            if hasattr(e, 'code'):
                print(e.code)
            print(e.errno)
            login()
            continue
        except ConnectionResetError as e:
            print('ConnectionResetError when read:'+url)
            time.sleep(10)
            login()
            continue
        except Exception as e:
            print('i do not know what is wrong. When readFromUrl()!')
            print(("url = "+url))
            print(traceback.format_exc())
            if hasattr(e, 'code'):
                print("Error Msg: "+e.code)
            time.sleep(3)
            login()
            continue
        
#end def readFromUrl
#--------------------------------------------------
#从url读取response
def responseFromUrl(url, formdata = None, headers = None):
    response = None
    if formdata != None:
        formdata = urllib.parse.urlencode(formdata)
    if headers == None:
        headers = getRandomHeaders()
    loopCount = 0
    #proxyNumber = len(proxyList)
    while True:
        loopCount += 1
        if loopCount > 5:
            print('Failed when trying responseFromUrl().')
            print(('URL = '+url))
            break
        try:
            req = urllib.request.Request(url, formdata, headers)
            #proxyNo = randint(0, proxyNumber-1)
            #req.set_proxy(proxyList[proxyNo], 'http')
            response = urllib.request.urlopen(req)
            curUrl = response.geturl()
            if(url != curUrl):
                #log.write('original url: '+url+'\n')
                #log.write('current  url: '+curUrl+'\n')
                if(curUrl == 'http://www.renrendai.com/exceptions/refresh-too-fast.jsp'):
                    print('Refresh too fast! Wait, login and retry...')
                    time.sleep(30)
                    login()
                    continue
            break
        except urllib.error.HTTPError as e:
            print("HTTP error code "+str(e.code))
            continue
        except (urllib.error.URLError) as e:
            if hasattr(e, 'code'):
                print(('ERROR:'+str(e.code)+' '+str(e.reason)))
                if(e.code == 404):
                    print(('url = '+url))
                    return None
            else:
                print((str(e.reason)))
            print(('url = '+url))
        except http.client.HTTPException as e:
            print("http exception.")
            continue
        except http.client.IncompleteRead as e:
            print(('[ERROR]IncompleteRead! '+url))
            continue
        except ssl.SSLError as e:
            print('[ERROR]ssl error!')
            continue
        except:
            print(('some error: '+url))
            login()
            continue
            
        if(response == None):
            print('responseFromUrl get a None')
            time.sleep(1)
            login()
            continue
    #end while
    
    return response
#--------------------------------------------------
def analyzeData(webcontent, writers):
    #print("content length:"+str(len(webcontent)))
    
    soup = BeautifulSoup(webcontent)
    
    if soup.find('img', {'src':'/exceptions/network-busy/img/404.png'}):
        return False #页面404
    if soup.find('img', {'src':'/exceptions/network-busy/img/500.png'}):
        return False #服务器发生错误
    
    currentDate = getTime('%Y/%m/%d')
    currentClock = getTime('%H:%M:%S')
    currentTime = getTime('%Y/%m/%d %H:%M:%S')
    
    ### 分析script ###
    jsonString = soup.find(id = 'credit-info-data').get_text()
    '''
    try:
        jsonString = soup.find(id = 'credit-info-data').get_text()
    except AttributeError as e:
        print("Attribute error.")
        print(webcontent)
        return False
    '''
    if jsonString == None:
        print('Cannot get json')
        return True
    #jsonString = jsonString.replace('"[', '[').replace(']"', ']') #多余引号导致分析错误
    #print jsonString
    scriptData = json.loads(jsonString)
    '''
    try:
        scriptData = json.loads(jsonString)
    except ValueError as e:
        print("ValueError")
        print(webcontent)
        return False
    '''
    ###本次借款基本信息###
    loanData = scriptData['data']['loan']
    loanId = loanData['loanId']
    tag_loanType = loanData['displayLoanType']
    if tag_loanType == 'SDRZ':
        loanType = '"实"'
    elif tag_loanType == 'XYRZ':
        loanType = '"信"'
    elif tag_loanType == 'JGDB':
        loanType = '"保"'
    else:
        loanType = tag_loanType
    tag_guarantor = loanData['utmSource']
    if tag_guarantor == 'debx-zdsd':
        guarantor = '"证大速券"'
    elif tag_guarantor == 'debx-yx':
        guarantor = '"友众信业"'
    elif tag_guarantor == 'debx-zaxy':
        guarantor = '"中安信业"'
    elif tag_guarantor == 'from-website':
        guarantor = ''
    elif tag_guarantor == 'debx-as':
        guarantor = '"安盛"'
    else:
        guarantor = '"'+tag_guarantor+'"'
    if loanData['title']:
        title = '"'+loanData['title']+'"'
    else:
        title = ''
    if loanData['borrowType']:
        borrowType = '"'+loanData['borrowType']+'"'
    else:
        borrowType = ''
    amount = loanData['amount']
    interest = loanData['interest']
    months = loanData['months']
    if loanData['status']:
        statusType = '"'+loanData['status']+'"'
    else:
        statusType = ''
    userId = loanData['borrowerId']
    if loanData['nickName']:
        username = '"'+loanData['nickName']+'"'
    else:
        username = ''
    borrowerLevel = loanData['borrowerLevel']
    leftMonths = loanData['leftMonths'] #剩余期数（月）
    finishedRatio = loanData['finishedRatio'] #完成额度
    if loanData['description']:
        description = '"'+loanData['description']+'"'
    else:
        description = ''
    if loanData['jobType']:
        jobType = '"'+loanData['jobType']+'"'
    else:
        jobType = ''
    originTimeFormat = '%b %d, %Y %I:%M:%S %p' #script中原始的时间格式
    openTime = beginBidTime = readyTime = passTime = startTime = closeTime = ''
    openTimeStr = loanData['openTime'] #开放时间
    #openTimeFormat = time.strptime(openTimeStr,'%b %d, %Y %I:%M:%S %p')
    #openTime = time.strftime('%Y/%m/%d %H:%M:%S', openTimeFormat) #开放日期
    #openTimeClock = time.strftime('%H:%M:%S', openTimeFormat)#开放时刻
    openTime = str2Datetime(openTimeStr, originTimeFormat)
    
    if 'beginBidTime' in list(loanData.keys()):
        beginBidTimeStr = loanData['beginBidTime'] #开始投标时间
        beginBidTime = str2Datetime(beginBidTimeStr, originTimeFormat)
        #beginBidTimeFormat = time.strptime(beginBidTimeStr, '%b %d, %Y %I:%M:%S %p')
    if 'readyTime' in list(loanData.keys()):
        readyTimeStr = loanData['readyTime'] #满标时间
        readyTime = str2Datetime(readyTimeStr, originTimeFormat)
    if 'passTime' in list(loanData.keys()):
        passTimeStr = loanData['passTime'] #可能为资金转移时间
        passTime = str2Datetime(passTimeStr, originTimeFormat)
    if 'startTime' in list(loanData.keys()):
        startTimeStr = loanData['startTime'] #不知道是什么
        startTime = str2Datetime(startTimeStr, originTimeFormat)
    if 'closeTime' in list(loanData.keys()):
        closeTimeStr = loanData['closeTime'] #还清时间
        closeTime = str2Datetime(closeTimeStr, originTimeFormat)
    
    status = ''
   
    if statusType == '"IN_PROGRESS"':
        status = '"'+'还款中'+'"'
    elif statusType == '"FIRST_READY"':
        status = '"'+'已满标'+'"'
    elif statusType == '"FIRST_APPLY"':
        status = '"'+'申请中'+'"'
    elif statusType == '"FAILED"':
        status = '"'+'已流标'+'"'
    elif statusType == '"BAD_DEBT"':
        status = '"'+'已垫付'+'"'
    elif statusType == '"CLOSED"':
        status = '"'+'已还清'+'"'
    else:
        status = '"'+statusType+'"'
    buffer1 = [currentTime, loanId, loanType, guarantor, title, amount, interest, months, openTime, beginBidTime, readyTime, passTime, startTime, closeTime, status]
    #print(buffer1)

    #soup = soup.find('body') #只从body中提取数据，出现了莫名截断的问题
    #print soup
    
    guaranteeType = repayTyep = ''
    prepaymentRate = repayEachMonth = '0'
    #保障方式
    tag_guaranteeType = soup.find('span', text = '保障方式')
    if tag_guaranteeType:
        guaranteeType = tag_guaranteeType.find_next_sibling('span').contents[0]
        #print guaranteeType
        guaranteeType = '"'+guaranteeType+'"'
    #还款方式
    tag_repayType = soup.find('span', text='还款方式')
    if tag_repayType:
        repayType = tag_repayType.find_next_sibling('span').contents[0]
        repayType = '"'+repayType+'"'
        #print repayType
    #提前还款费率
    tag_prepaymentRate = soup.find('span', text='提前还款费率')
    if tag_prepaymentRate:
        prepaymentRate = tag_prepaymentRate.find_next_sibling('span').find('em').string
        #print prepaymentRate
    #月还本息    
    tag_repayEachMonth = soup.find('span', text='月还本息（元）')
    if tag_repayEachMonth:
        repayEachMonth = tag_repayEachMonth.find_next_sibling('span').find('em').string
        repayEachMonth = repayEachMonth.replace(',', '')
        #print repayEachMonth
    #待还本息
    amountToRepay = 0
    tag_amountToRepay = soup.find('em', text=re.compile('待还本息\w*'))
    if tag_amountToRepay:
        amountToRepay = tag_amountToRepay.find_next_sibling('span').string.replace(',', '')
        amountToRepay = re.search(r'\d+', amountToRepay).group()
        #去掉单位
        amountToRepay = amountToRepay.replace('元','')
    #print amountToRepay
    #满标用时
    fullTime = ''
    tag_fullTime = soup.find('span', {'id':'fullTime'})
    if tag_fullTime:
        fullTime = tag_fullTime['data-time']
    buffer1.extend([guaranteeType, prepaymentRate, repayType, repayEachMonth, finishedRatio, fullTime])
    #print buffer1
    
    ###用户个人信息###
    #tag_userinfo = soup.find('table', class_='ui-table-basic-list')#ui-table-basic-list
    tag_userinfo = soup.find('div', {'class':'ui-tab-content-basic'})#ui-tab-content-info
    
    #2015-11-1 by lyq: 网页结构变化，由list变成了table
    list_td = tag_userinfo.find('table').find_all('td')
    
    age = list_td[3].em.get_text() #年龄
    education = list_td[4].em.get_text()#学历
    if education=='--': education=''
    else:
        education = '"'+education+'"'
    marriage = list_td[5].em.get_text()#婚姻
    if marriage.find('--')>=0: marriage = ''
    else:
        marriage = '"'+marriage+'"'
    incomeRange = list_td[17].em.get_text()#收入
    if incomeRange == '--': incomeRange = ''
    else:
        incomeRange = incomeRange.replace('元', '')
    house = list_td[18].em.get_text().strip() #房产
    house = '"'+house+'"'
    houseLoan = list_td[19].em.get_text().strip() #房贷 '"'+ +'"'
    houseLoan = '"'+houseLoan +'"'
    car = list_td[20].em.get_text().strip()#车产
    car = '"'+ car +'"'
    carLoan = list_td[21].em.get_text().strip()#车贷
    carLoan = '"'+carLoan +'"'
    company = list_td[23].em.get_text()
    if company == '--': company = ''
    else:
        company = '"'+company +'"'
    companyScale = list_td[24].em.get_text()#公司规模
    if companyScale == '--': companyScale = ''
    else:
        companyScale = companyScale.replace('人', '')
    '''
    city = list_td[25].em.get_text()#工作城市
    if city.find('请选择')>=0 or city.find('--')>=0: 
        city = ''
    workTime = list_td[26].em.get_text()#工作时间
    if workTime=='--': workTime = ''
    position = list_td[27].em.get_text()#岗位职位
    if position == '--': position = ''
   '''
    city = ''
    workTime = ''
    position = '' #目前这三个数据挖不倒
    
    userinfo = [userId, username.encode('gbk', 'ignore').decode('gbk'), age, education, marriage, company, companyScale, position,city, workTime, incomeRange, house, houseLoan, car, carLoan, jobType]
    buffer1.extend(userinfo)
    
    ###信用档案###
    creditRank = list_td[1].find('em').find('i')['class'] #信用评级
    if creditRank:
        creditRank = creditRank[1]
    creditScore = list_td[1].find('em')['title'] #信用评分
    if creditScore:
        creditScore = ''.join(filter(str.isdigit, str(creditScore.strip()))) #提取数字
    loanTimes = list_td[7].em.get_text()#申请借款
    if loanTimes:
        loanTimes = ''.join(filter(str.isdigit, str(loanTimes.strip()))) #提取数字
    creditLine = list_td[8].em.get_text()#信用额度
    if creditLine:
        creditLine = creditLine.replace('元','')
    overdueAmount = list_td[9].em.get_text()#逾期金额
    if overdueAmount:
        overdueAmount = overdueAmount.replace('元','')
    loanSuccessTimes = list_td[10].em.get_text()#成功借款
    if loanSuccessTimes:
        loanSuccessTimes = ''.join(filter(str.isdigit, str(loanSuccessTimes.strip()))) #提取数字
    loanTotalAmount = list_td[11].em.get_text()#借款总额
    if loanTotalAmount:
        loanTotalAmount = ''.join(filter(str.isdigit, str(loanTotalAmount.strip()))) #提取数字
    overdueTimes = list_td[12].em.get_text()#逾期次数
    if overdueTimes:
        overdueTimes = ''.join(filter(str.isdigit, str(overdueTimes.strip()))) #提取数字
    payoffTimes = list_td[13].em.get_text()#还清笔数
    #转换成数字
    if payoffTimes:
        payoffTimes = ''.join(filter(str.isdigit, str(payoffTimes.strip())))
    torepayAmount = list_td[14].em.get_text()#待还本息
    if torepayAmount:
        torepayAmount = torepayAmount.replace('元','')
    seriousOverdueTimes = list_td[15].em.get_text()#严重逾期
    if seriousOverdueTimes:
        seriousOverdueTimes = seriousOverdueTimes.replace('笔','')
    creditRecord = [creditRank, creditScore, loanTimes, loanSuccessTimes, payoffTimes, creditLine, loanTotalAmount, torepayAmount, overdueAmount, overdueTimes, seriousOverdueTimes]
    buffer1.extend(creditRecord)

    ###审核信息###
    list_renzheng = ['credit', 'identificationScanning', 'work', 'incomeDuty', 'house', 'car', 'marriage', 'graduation', 'fieldAudit', 'mobileReceipt', 'kaixin', 'residence', 'video']
    #"creditInfo":{"creditInfoId":490655,"user":495364,"identificationScanning":"VALID","mobile":"INVALID","graduation":"INVALID","credit":"OVERDUE","residence":"INVALID","marriage":"INVALID","child":"INVALID","album":"INVALID","work":"OVERDUE","renren":"INVALID","kaixin":"INVALID","house":"INVALID","car":"INVALID","identification":"VALID","detailInformation":"INVALID","borrowStudy":"VALID","mobileReceipt":"INVALID","incomeDuty":"OVERDUE","other":"INVALID","account":"INVALID","titles":"INVALID","fieldAudit":"INVALID","mobileAuth":"INVALID","video":"INVALID","version":1}
    creditInfo = scriptData['data']['creditInfo']
    list_creditInfo = {'credit':'', 'identificationScanning':'', 'work':'', 'incomeDuty':'', 'house':'', 'car':'', 'marriage':'', 'graduation':'', 'fieldAudit':'', 'mobileReceipt':'', 'kaixin':'', 'residence':'', 'video':''}
    #kaixin为微博，技术职称认证不详暂为fieldAudit
    for item in list(creditInfo.keys()):
        if(creditInfo[item] == 'INVALID'):
            list_creditInfo[item] = ''
        elif(creditInfo[item] == 'VALID'):
            list_creditInfo[item] = '1'
        else:
            list_creditInfo[item] = '0' #其他情况说明没通过，如pending或failed，250009
    ###审核通过时间###
    #"creditPassedTime":{"creditPassedTimeId":77028,"user":77078,"credit":"Dec 26, 2011 12:58:55 PM","work":"Dec 19, 2011 2:47:29 PM","incomeDuty":"Dec 22, 2011 1:34:36 PM","identificationScanning":"Dec 17, 2011 1:43:35 PM","marriage":"Dec 19, 2011 9:55:20 AM"}
    creditPassedTime = scriptData['data']['creditPassedTime']
    #信用报告，工作认证，收入认证，身份认证，婚姻认证
    list_passedTime = {'credit':'', 'identificationScanning':'', 'work':'', 'incomeDuty':'', 'house':'', 'car':'', 'marriage':'', 'graduation':'', 'fieldAudit':'', 'mobileReceipt':'', 'kaixin':'', 'residence':'', 'video':''}
    for item in list(creditPassedTime.keys()):
        try:
            passedTime = time.strptime(creditPassedTime[item],'%b %d, %Y %I:%M:%S %p')
            list_passedTime[item] = time.strftime('%Y-%m-%d', passedTime)
            list_creditInfo[item] = 1 #通过的也认为已经认证了
        except:
            continue
    data_renzheng = []
    for i in range(0, len(list_renzheng)):
        itemName = list_renzheng[i]
        data_renzheng.append(list_creditInfo[itemName])
        data_renzheng.append(list_passedTime[itemName])
        #print list_renzheng[i]+': '+list_creditInfo[list_renzheng[i]]+' '+list_passedTime[list_renzheng[i]]
    buffer1.extend(data_renzheng)
    buffer1.append(description)
    
    for index, item in enumerate(buffer1):
        if(isinstance(item, str)):
            item = item.encode('gbk', 'ignore').decode('gbk')
            buffer1[index] = item
    writers[0].writerow(buffer1)
    
    basicInfo = [currentTime]
    #投标记录-----------------------------------------
    analyzeLenderData(loanId, writers[1], basicInfo)
    
    #还款表现-----------------------------------------
    analyzeRepayData(loanId, writers[2], basicInfo)
    
    #催收信息-----------------------------------------
    analyzeCollectionData(loanId, writers[7], basicInfo)
    
    #债权信息-----------------------------------------
    analyzeLenderInfoData(loanId, writers[3], basicInfo)
    
    #债券转让记录-------------------------------------
    analyzeTransferData(loanId, writers[4], basicInfo)
    
    #用户信息---------------------------------------
    analyzeUserData(userId, writers[5], [loanTimes, loanSuccessTimes, payoffTimes, overdueTimes, overdueAmount, seriousOverdueTimes])
    
    #评论信息---------------------------------
    #print('  Get Comments...')
    #新的网页中暂时没有出现评论信息
    '''
    commentPage = 0
    while True:
        commentPage += 1
        if(commentPage > 1):
            commentsString = readFromUrl(urlCommentPrefix+str(loanId)+'&pageIndex='+str(commentPage))
            #print commentsString
            if(len(commentsString) == 0):
                break
        else:
            commentsString = soup.find('script', {'id':'comments-data'}).get_text()
        commentsJson = json.loads(commentsString)
        list_comments = commentsJson['data']['loanComments']
        for item in list_comments:
            m1 = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['commentTime'])
            if m1:
                commentDate = m1.group(1)
                commentClock = m1.group(2)
            else:
                commentFullTime = time.strptime(item['commentTime'],'%b %d, %Y %I:%M:%S %p')
                commentDate = time.strftime('%Y-%m-%d', commentFullTime)
                commentClock = time.strftime('%H:%M:%S', commentFullTime)
            comment = [currentDate, currentClock]
            comment.extend([item['toLoanId'], item['byUserId'], item['displayName'].encode('gbk', 'ignore').decode('gbk'), commentDate,commentClock, item['content']])
            if 'repliedComments' in item:
                if item['repliedComments'] != None:
                    reply = item['repliedComments'][0]
                    m2 = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', reply['commentTime'])
                    if m2:
                        replyDate = m2.group(1)
                        replyClock = m2.group(2)
                    else:
                        replyFullTime = time.strptime(reply['commentTime'],'%b %d, %Y %I:%M:%S %p')
                        replyDate = time.strftime('%Y-%m-%d', replyFullTime)
                        replyClock = time.strftime('%H:%M:%S', replyFullTime)
                    replyUserId = reply['byUserId']
                    replyContent = reply['content']
                    comment.extend([reply['byUserId'], reply['displayName'].encode('gbk', 'ignore').decode('gbk'), replyDate, replyClock, reply['content']])
                    
            for index, item in enumerate(comment):
                if(isinstance(item, str)):
                    item = item.encode('gbk', 'ignore').decode('gbk')
                    comment[index] = item
            writers[6].writerow(comment)
        if(len(list_comments) < 10):
            break
    '''
    
    return True
    
#---------------------------------------------
def analyzeLenderData(loanId, writer, attrs):
    ###js获得投标记录###
    #print('  Get Lender Records...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        lenderRecordsString = readFromUrl(urlLenderRecordsPrefix+str(loanId))
        if(lenderRecordsString != "null"):break
    #end while
    if(lenderRecordsString == "null"):
        print((str(loanId)+" lenderRecord Error!"))
        return
    #lenderRecordsString = readFromUrl(urlLenderRecordsPrefix+str(loanId))
    lenderRecords = json.loads(lenderRecordsString)
    #print str(loanId)+" lenderRecord:"
    #print lenderRecordsString
    list_lenderRecords = lenderRecords['data']['lenderRecords']
    #print list_lenderInfo
    for item in list_lenderRecords:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['lendTime'])
        lendDate = m.group(1)
        lendClock = m.group(2)
        lendTime = str2Datetime(item['lendTime'], '%Y-%m-%dT%H:%M:%S')
        lenderType = '"无"' #投标类型：理、自、U、无
        financePlanId = '' #理财计划期数或U计划类型
        if(item['lenderType'] == 'FINANCEPLAN_BID'):#FINANCEPLAN_BID or NORMAL_BID or AUTO_BID
            financePlanId = item['financeCategory']
            lenderType = '"U"'
            if financePlanId == 'OLD':
                financePlanId = item['financePlanId']
                lenderType = '"理"'
        elif(item['lenderType'] == 'AUTO_BID'):
            lenderType = '"自"'
            
        mobileTrade = '0'
        if(item['tradeMethod'] == 'MOBILE'):
            mobileTrade = '1'
        if item['userNickName']:
            username = '"'+item['userNickName'].encode('gbk', 'ignore').decode('gbk')+'"'
        else:
            username = ''
        buffer_lenderRecords = []
        buffer_lenderRecords.extend(attrs)
        buffer_lenderRecords.extend([item['loanId'], item['userId'], username, mobileTrade, item['amount'], lendTime, lenderType, financePlanId])
        #print buffer_lenderRecords
        for index, item in enumerate(buffer_lenderRecords):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_lenderRecords[index] = item
        writer.writerow(buffer_lenderRecords)
#end def analyzeLenderData
#-------------------------------------------------
def analyzeRepayData(loanId, writer, attrs):
    #print('  Get Repay Log...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        repayDetailString = readFromUrl(urlRepayDetailPrefix+str(loanId))
        if(repayDetailString != "null"):break
    #end while
    if(repayDetailString == "null"):
        print((str(loanId)+" repayDetail Error!"))
        return
    repayDetail = json.loads(repayDetailString)
    #print str(loanId)+" repayDetail:"
    #print repayDetailString
    totalunRepaid = repayDetail['data']['unRepaid']
    totalRepaid = repayDetail['data']['repaid']
    list_repayDetail = repayDetail['data']['phases']
    for item in list_repayDetail:
        repayTime = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['repayTime']).group(1)
        if item['actualRepayTime']:
            actualRepayTime = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['actualRepayTime']).group(1)
        else:
            actualRepayTime = ''
        buffer_repayDetail = []
        buffer_repayDetail.extend(attrs)
        repaytype = item['repayType']
        if repaytype:
            repaytype = '"'+repaytype+'"'
        buffer_repayDetail.extend([loanId, repayTime, repaytype, item['unRepaidAmount'], item['repaidFee'], actualRepayTime])
        
        for index, item in enumerate(buffer_repayDetail):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_repayDetail[index] = item
        writer.writerow(buffer_repayDetail)
    
#end def analyzeRepayData
#-------------------------------------------------
def analyzeCollectionData(loanId, writer, attrs):
    #print('  Get Collection Log...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        collectionString = readFromUrl(urlCollectionPrefix+str(loanId));
        if(collectionString != "null"):break
    #end while
    if(collectionString== "null"):
        print((str(loanId)+" collectionString Error!"))
        return
    #collectionString = readFromUrl(urlCollectionPrefix+str(loanId));
    collectionInfo = json.loads(collectionString)
    list_collection = collectionInfo['data']['dunInfoList']
    for item in list_collection:
        time = ''
        if item['dunTime']:
            time = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['dunTime']).group(1)
        elif item['createTime']:
            time = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime']).group(1)
        contact =  item['contact']
        if contact:
            contact = '"'+contact+'"'       
        description = item['description']
        if description:
            description = '"'+description+'"'
        buffer_collection = []
        buffer_collection.extend(attrs)
        buffer_collection.extend([loanId, time, contact, description])
        
        for index, item in enumerate(buffer_collection):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_collection[index] = item
        writer.writerow(buffer_collection)
#end def analyzeCollectionData()
#---------------------------------------------------
def analyzeLenderInfoData(loanId, writer, attrs):
    ###js获得债权信息###
    #print('  Get Lender Infomation...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        lenderInfoString = readFromUrl(urlLenderInfoPrefix+str(loanId))
        if(lenderInfoString != "null"):break
    #end while
    if(lenderInfoString == "null"):
        print((str(loanId)+" lenderInfo Error!"))
        return
    #lenderInfoString = readFromUrl(urlLenderInfoPrefix+str(loanId))
    #log.write('[lender Info String] '+str(loanId)+'\n'+lenderInfoString+'\n\n')
    lenderInfo = json.loads(lenderInfoString)
    list_lenderInfo = lenderInfo['data']['lenders']
    #print list_lenderInfo
    for item in list_lenderInfo:
        lenderType = '"无"' #投标类型：理、U、无
        financePlanId = '' #理财计划期数或U计划类型
        if(item['financePlanId'] != None):
            financePlanId = item['financePlanCategory']
            lenderType = '"U"'
            if financePlanId == 'OLD':
                financePlanId = item['financePlanId']
                lenderType = '"理"'
        
        if item['nickName']:
            username = '"'+item['nickName'].encode('gbk', 'ignore').decode('gbk')+'"'
        else:
            username = ''
            
        buffer_lenderInfo = []
        buffer_lenderInfo.extend(attrs)
        buffer_lenderInfo.extend([loanId, item['userId'], username, item['leftAmount'], item['share'], lenderType, financePlanId])
        
        for index, item in enumerate(buffer_lenderInfo):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_lenderInfo[index] = item
        writer.writerow(buffer_lenderInfo)
#end def analyzeLenderInfoData()

#---------------------------------------------------
def analyzeTransferData(loanId, writer, attrs):
###js获得债券转让记录###
    #print('  Get Transfer Log...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        transferLogString = readFromUrl(urlTransferLogPrefix+str(loanId))
        if(transferLogString != "null"):break
    #end while
    if(transferLogString == "null"):
        print((str(loanId)+" transferLog Error!"))
        return
        
    #transferLogString = readFromUrl(urlTransferLogPrefix+str(loanId))
    transferLog = json.loads(transferLogString)
    
    transferAccount = transferLog['data']['account']
    transferNoAccount = transferLog['data']['noAccount']
    list_transferLog = transferLog['data']['loanTransferLogList']
    for item in list_transferLog:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        transferDate = m.group(1)
        transferClock = m.group(2)
        transferTime = str2Datetime(item['createTime'], '%Y-%m-%dT%H:%M:%S')
        
        if item['toUserId']:
            username = '"'+item['toUserId'].encode('gbk', 'ignore').decode('gbk')+'"'
        else:
            username = ''
    
        if item['fromUserId']:
            fromnickname = '"'+item['fromUserId'].encode('gbk', 'ignore').decode('gbk')+'"'
        else:
            fromnickname = ''
        buffer_transferLog = []
        buffer_transferLog.extend(attrs)
        buffer_transferLog.extend([loanId, username, item['toNickName'], fromnickname, item['fromNickName'], item['fromFinancePlanId'], item['price'], item['share'], transferTime])
        
        for index, item in enumerate(buffer_transferLog):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_transferLog[index] = item
        writer.writerow(buffer_transferLog)
#end def analyzeTransferData()
#-------------------------------------------------------
def analyzeUserData(userId, writer, attrs):
    #print('  Get User Info...')
    content_user = readFromUrl(urlUserPrefix+str(userId))
    soup = BeautifulSoup(content_user)
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    currentTime = getTime('%Y-%m-%d %H:%M:%S')
    #个人信息
    nickName = soup.find('span', {'id':'nick-name'}).string
    if nickName:
        nickName = '"'+nickName+'"'
    tag_registerDate = soup.find('div', class_='avatar-info')
    if tag_registerDate:
        registerDate = re.search('\d+-\d+-\d+', tag_registerDate.find('p').string).group(0)
    #理财统计
    ownInfo = soup.find('div', class_='avatar-invest')
    tag_ownBondsCount = ownInfo.dl.find('dd')
    ownBondsCount = tag_ownBondsCount.find('em').string
    if ownBondsCount:
        ownBondsCount = ownBondsCount.replace('笔','')
    tag_ownFinancePlansCount = tag_ownBondsCount.find_next('dd')
    
    ownFinancePlansCount = tag_ownFinancePlansCount.find('em').string
    if ownFinancePlansCount:
        ownFinancePlansCount = ownFinancePlansCount.replace('笔','')
    
    buffer_user = [currentTime, userId, nickName, registerDate, ownBondsCount, ownFinancePlansCount]
    buffer_user.extend(attrs)
    
    for index, item in enumerate(buffer_user):
        if(isinstance(item, str)):
            item = item.encode('gbk', 'ignore').decode('gbk')
            buffer_user[index] = item
    writer.writerow(buffer_user)
#end analyzeUserData()

#------------------------------------------------------
def analyzeUPData(webcontent, planId, writers):
    print(('planID='+str(planId)))
    soup = BeautifulSoup(webcontent)
    currentDate = getTime('%Y-%m-%d')
    currentClock = getTime('%H:%M:%S')
    currentTime = getTime('%Y-%m-%d %H:%M:%S')
    tag_basic = soup.find('div', {'id':'plan-basic-panel'})
    if tag_basic == None:
        return False
    planInfo = tag_basic.find('div', class_='planinfo')
    
    list_basic1 = planInfo.find('div').find_all('dl', class_='fn-left')
    planAmount = list_basic1[0].find('span').get_text() #计划金额
    '''
    if planAmount:
        planAmount = ''.join(filter(str.isdigit, str(planAmount.encode('utf-8')))) #只保留数字
   '''
    expectedRate = list_basic1[1].find('span').get_text()+'%' #预期年化收益
    #lockPeriod = list_basic1[2].em.get_text() #锁定期限
    
    list_basic2 = planInfo.ul.find_all('li', class_='fn-clear')
    list_span1 = list_basic2[0].find_all('span')
    #planProducts = list_span1[1]['data-products'] #投标范围
    guaranteeMode = list_span1[1].get_text().replace(u"\uf046", "") #保障方式，后面有一个\uf046无法转为GBK
    if guaranteeMode:
        guaranteeMode = '"'+guaranteeMode+'"'
    #print(guaranteeMode.replace(u"\uf046", ""))
    #list_span2 = list_basic2[1].find_all('span')
    #lockDate = list_span2[1].get_text() #退出日期/锁定日期
    #addLimit = list_span2[3].em.get_text() #加入上限
    
    incomeGet = ' '
    wholeTime = ' '
    
    planReserve = tag_basic.find('div',class_='plan-reserve')
    if planReserve:
        wholeTime = planReserve.find('div',class_='box-top').find('span').get_text()#满额用时
    
    planIncome = tag_basic.find('div',class_='plan-income')
    if planIncome:
        incomeGet = planIncome.find('div',class_='box-top').find('span').get_text()#满额用时


    statusTemp = soup.find('div', class_='stamp');
    if statusTemp:
        statusTag = soup.find('div', class_='stamp').em
        statusCode = '"等待预定"'
        if statusTag:
            statusCode = statusTag['class'][0]
        status = statusCode
        if(statusCode == 'INCOME'): status = '"收益中"'
        elif(statusCode == 'RESERVE'): status = '"预定满额"'
        elif(statusCode == 'OPEN'): status = '"开放期"'
        elif(statusCode == 'PLAN'): status = '"计划满额"'
    else:
        status = '"等待加入"';
    '''
    statusTag = soup.find('div', class_='stamp').em
    statusCode = '等待预定'
    if statusTag:
        statusCode = statusTag['class'][0]
    status = statusCode
    if(statusCode == 'INCOME'): status = '收益中'
    elif(statusCode == 'RESERVE'): status = '预定满额'
    elif(statusCode == 'OPEN'): status = '开放期'
    elif(statusCode == 'PLAN'): status = '计划满额'
    '''
    planTab = soup.find('div', {'id':'plan-tab-content'})
    list_tr = planTab.find('tbody').find_all('tr')
    planName = list_tr[0].td.get_text() #名称
    if planName:
        planName = '"'+planName+'"'
    planProducts = list_tr[2].td.get_text() #投标范围
    if planProducts:
        planProducts = '"'+planProducts+'"'
    incomeHandleWay = list_tr[2].td.get_text() #收益处理方式
    if incomeHandleWay:
        incomeHandleWay = '"'+incomeHandleWay+'"'
    lockPeriod = list_tr[4].td.get_text() #锁定期
    lockPeriod = ''.join(filter(str.isdigit, str(lockPeriod.strip())))
    quitDate = list_tr[5].td.get_text() #退出日期
    joinCondition = list_tr[6].td.get_text() #加入条件
    if joinCondition:
        joinCondition = '"'+joinCondition+'"'
    joinLimit = list_tr[7].td.get_text() #加入上限
    if joinLimit:
        joinLimit = joinLimit.replace('元','')
    #界面修改导致的代码调整 2015-10-6
    joinStart = list_tr[8].td.get_text() #开时加入时间
    if joinStart:
        joinStart = '"'+joinStart+'"'
    list_Cost = list_tr[11].find_all('dd')
    '''
    earnest = list_tr[8].td.get_text() #定金
    reserveStart = list_tr[9].td.get_text() #预定开始时间
    payDeadline = list_tr[10].td.get_text() #支付截止时间
    joinStart = list_tr[11].td.get_text() #开放加入时间
    list_Cost = list_tr[14].find_all('dd')
    joinCost = list_Cost[0].font.get_text() #加入费用
    serviceCost = '0.00%' #管理/服务费用
    
    if list_Cost[1].font:
       serviceCost = list_Cost[1].font.get_text()
    '''
    joinCost = list_Cost[0].font.get_text(); #加入费用
    quitCost = list_Cost[2].font.get_text() #退出费用
    earlyquitCost = '0' #提前退出费用
    if len(list_Cost) > 3:
        earlyquitCost = list_Cost[3].font.get_text() 
    
    planDetails = soup.find('div', {'id':'plan-details'})
  
    planStep3 = planDetails.find('div', class_='step-three')
    lockStart = planStep3.find('p').get_text()
    if lockStart:
        lockStart = re.match('进入理财期(.*)', lockStart).group(1)
        if lockStart:
            lockStart = str2Datetime(lockStart, '%m月%d日 %H:%M', '%m/%d %H:%M')
    
    '''
    list_basicInfo = tag_basic.ul.find_all('li', class_='fn-clear')
    
    #planAmount = list_basicInfo[0].find('span', class_='num').em.get_text()
    #expectedRate = list_basicInfo[0].find('span', {'id':'expected-rate'})['data-value']
    #planProducts = list_basicInfo[1].find('span', {'id':'plan-basic-products'})['data-products']
    #guaranteeMode = list_basicInfo[1].find('span', class_='last').get_text()
    status = list_basicInfo[2].find('span', class_='basic-value').get_text()
    fullTime = list_basicInfo[2].find('span', class_='last').get_text()
    #lockPeriod = list_basicInfo[3].find('em', class_='value').get_text()
    lockDate = list_basicInfo[3].find('span', class_='last').get_text()
    #print list_basicInfo[4]
    buyInRate = list_basicInfo[5].find('div', {'id':'buy-in-rate'})['data-br']
    interestRate = list_basicInfo[5].find('div', {'id':'interest-rate'})['data-ir']
    quitRate = list_basicInfo[5].find('div', {'id':'quit-rate'})['data-qr']
    
    leftAmount = soup.find('em', {'id':'max-amount-1'})['data-amount']
    joinAmountLimit = soup.find('em', {'id':'max-amount-2'})['data-amount']
    '''
    buffer_UP = [currentTime, planName, planId, str(planAmount), expectedRate, planProducts,incomeHandleWay,incomeGet,wholeTime, guaranteeMode, status, str(lockPeriod), joinCondition, joinLimit, joinStart, lockStart, quitDate, joinCost, quitCost, earlyquitCost]
    #buffer_UP = [currentTime, planName, planId, str(planAmount), expectedRate, planProducts, guaranteeMode, status, str(lockPeriod), joinCondition, joinLimit, reserveStart, reserveStop, payDeadline, joinStart, lockStart, quitDate, joinCost, serviceCost, quitCost, earlyquitCost]
    #print(buffer_UP)
    
    
    
    #分析预定记录
    reserveInfo = analyzeReserve(planId, planName, writers[2])
    #分析加入记录
    joinInfo = analyzeUPLender(planId, planName, writers[3])
    #分析理财计划表现
    performance = analyzePlan(planId, planName)
    
    buffer_UP.extend(reserveInfo)
    buffer_UP.extend(joinInfo)
    buffer_UP.extend(performance)
    #print(buffer_UP)
    
    for index, item in enumerate(buffer_UP):
        if(isinstance(item, str)):
            item = item.encode('gbk', 'ignore').decode('gbk')
            buffer_UP[index] = item
    writers[1].writerow(buffer_UP)
    return True
#end def analyzeUPData()
#--------------------------------------------------------
#预定记录
def analyzeReserve(planId, planName, writer):
    content_reserve = readFromUrl(urlFPReservePrefix+str(planId))
    #print content_reserve
    reserveInfo = json.loads(content_reserve)
    list_reserve = reserveInfo['data']['rsvList']
    reserveNotpayAmount = 0
    for item in list_reserve:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        aDate = m.group(1)
        aClock = m.group(2)
        aTime = str2Datetime(item['createTime'], '%Y-%m-%dT%H:%M:%S')
        buffer_reserve = [planName, planId]
        tradeMethod = '"无"'
        if(item['tradeMethod'] == 'MOBILE'): tradeMethod = '"手机预定"'
        elif(item['ucodeId'] is not None): tradeMethod = '"U-code预定"'
        
        if(item['reserveType'] == '未支付'):
            reserveNotpayAmount += item['planAmount'] #计算未支付总额
        name = item['nickName'].encode('gbk', 'ignore').decode('gbk')
        if name:
            name = '"'+name+'"'
        restype = item['reserveType']
        if restype:
            restype = '"'+restype+'"'
        buffer_reserve.extend([name, item['userId'], item['planAmount'], aTime, tradeMethod, restype])
        #if(planId == 142): print(buffer_reserve)
        
        for index, item in enumerate(buffer_reserve):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_reserve[index] = item
        writer.writerow(buffer_reserve)
    return [len(list_reserve), reserveNotpayAmount]
#end def analyzeReserve
#--------------------------------------------------------
#加入记录, 返回总人数和总金额
def analyzeUPLender(planId, planName, writer):
    #print('  Get Lender Info...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        content_lender = readFromUrl(urlFPLenderPrefix+str(planId))
        if(content_lender != "null"):break
    #end while
    if(content_lender == "null"):
        print((str(planId)+" content_lender Error!"))
        return
        
    #content_lender = readFromUrl(urlFPLenderPrefix+str(planId))
    lenderInfo = json.loads(content_lender)
    
    list_lenders = lenderInfo['data']['jsonList']
    #print len(list_lenders)
    reserveHadpayAmount = 0 #加入金额
    for item in list_lenders:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        aDate = m.group(1)
        aClock = m.group(2)
        aTime = str2Datetime(item['createTime'], '%Y-%m-%dT%H:%M:%S')
        buffer_lender = [planName, planId]
        reserveHadpayAmount += item['amount']
        name = item['nickName'].encode('gbk', 'ignore').decode('gbk')
        if name:
            name = '"'+name+'"'
        buffer_lender.extend([name, item['userId'], item['amount'], aTime])
        
        for index, item in enumerate(buffer_lender):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_lender[index] = item
        writer.writerow(buffer_lender)
    return [len(list_lenders), reserveHadpayAmount]
#end def analyzeUPLender()
#----------------------------------------------------
def analyzePlan(planId, planName):
    #print('  Get Performace...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        content_plan = readFromUrl(urlFPPerformancePrefix+str(planId))
        if(content_plan != "null"):break
    #end while
    if(content_plan == "null"):
        print((str(planId)+" content_plan Error!"))
        return
        
    #content_plan = readFromUrl(urlFPPerformancePrefix+str(planId))
    planInfo = json.loads(content_plan)
    item = planInfo['data']['financePlanVos'][0]
    #print item
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')
    buffer_performance = []
    #reserveDateFormat = time.strptime(item['reserveDate'],u'%Y年%m月%d日')
    #reserveDate = time.strftime('%Y-%m-%d', reserveDateFormat)
    buffer_performance.extend([item['useTime'], item['bidCount'], item['earnInterest'], item['averageBidInterest'], item['borrowCount']])
    #writer.writerow(buffer_performance)
    return buffer_performance
#end def analyzePlan()
#---------------------薪计划数据分析---------------------------------
# add by Li Yanqing at 2015-10-07
def analyzeSPData(webcontent, planId, writers):
    print(('planID='+str(planId)))
    soup = BeautifulSoup(webcontent)
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')
    currentTime = getTime('%Y-%m-%d %H:%M:%S')
    tag_basic = soup.find('div', {'id':'autoinvest-basic-panel'})
    if tag_basic == None:
        return False
    planInfo = tag_basic.find('div', class_='planinfo')
    
    list_basic1 = planInfo.find('div').find_all('dl', class_='fn-left')
    #planAmount = list_basic1[0].em.get_text() #计划金额
    leftCount = list_basic1[2].find('span').get_text() #剩余名额
    
    list_basic2 = planInfo.find('ul').find_all('li', class_='fn-clear')
    list_span1 = list_basic2[0].find_all('span')
    guaranteeMode = list_span1[2].get_text().replace(u"\uf046", "") #保障方式，后面有一个\uf046无法转为GBK
    if guaranteeMode:
        guaranteeMode = '"'+guaranteeMode +'"'
   
    incomeGet = ' '
    wholeTime = ' '
    
    planReserve = tag_basic.find('div',class_='plan-reserve')
    if planReserve:
        wholeTime = planReserve.find('div',class_='box-bottom').find('span').find('i').get_text()#满额用时
    
    planIncome = tag_basic.find('div',class_='plan-income')
    if planIncome:
        incomeGet = planIncome.find('div',class_='box-bottom').find('span').find('i').get_text()#满额用时
    
    
    statusTemp = soup.find('div', class_='stamp');
    if statusTemp:
        statusTag = soup.find('div', class_='stamp').em
        statusCode = '"等待预定"'
        if statusTag:
            statusCode = statusTag['class'][0]
        status = statusCode
        if(statusCode == 'INCOME'): status = '"收益中"'
        elif(statusCode == 'RESERVE'): status = '"预定满额"'
        elif(statusCode == 'OPEN'): status = '"开放期"'
        elif(statusCode == 'PLAN'): status = '"计划满额"'
    else:
        status = '"等待加入"';
    planTab = soup.find('div', {'id':'autoinvest-tab-content'})
    list_tr = planTab.find('tbody').find_all('tr')
    planName = list_tr[0].td.get_text() #名称
    if planName:
        planName = '"'+planName+'"'
    planProducts = list_tr[2].td.get_text() #投标范围
    if planProducts:
        planProducts = '"'+planProducts+'"'
    incomeHandleWay = list_tr[3].td.get_text() #收益处理方式
    if incomeHandleWay:
        incomeHandleWay = '"'+incomeHandleWay+'"'
    expectedRate = list_tr[4].td.get_text() #预期年化收益
    investmentDay = list_tr[5].td.get_text() #每月投资日
    if investmentDay:
        investmentDay = '"'+investmentDay+'"'
    monthInvestmentAmount = list_tr[6].td.get_text() #月投资金额
    if monthInvestmentAmount:
        monthInvestmentAmount = '"'+monthInvestmentAmount+'"'
    rangeTime = list_tr[8].td.get_text() #理财期限
    if rangeTime:
        rangeTime = ''.join(filter(str.isdigit,str(rangeTime.strip())))
    quitDate = list_tr[9].td.get_text() #到期日
    earlyQuit = list_tr[11].td.get_text() #提前退出
    if earlyQuit:
        earlyQuit = '"'+earlyQuit.replace('*','')+'"'

   
    list_Cost = list_tr[12].find_all('dd')
    joinCost = list_Cost[0].font.get_text(); #加入费用
    quitCost = list_Cost[2].font.get_text() #退出费用
    
    
 
    buffer_UP = [currentTime, planName, planId, str(leftCount), expectedRate, planProducts, guaranteeMode, status, str(incomeHandleWay), rangeTime,incomeGet, wholeTime, investmentDay, quitDate, joinCost, quitCost, monthInvestmentAmount,earlyQuit]
    
    
    #分析预定记录
    #reserveInfo = analyzeReserve(planId, planName, writers[2])
    #分析加入记录
    joinInfo = analyzeSPBuyer(planId, planName, writers[3])
    #分析理财计划表现
    performance = analyzeSPlan(planId, planName)
    
    #buffer_UP.extend(reserveInfo)
    buffer_UP.extend(joinInfo)
    buffer_UP.extend(performance)
    #print(buffer_UP)
    
    for index, item in enumerate(buffer_UP):
        if(isinstance(item, str)):
            item = item.encode('gbk', 'ignore').decode('gbk')
            buffer_UP[index] = item
    writers[1].writerow(buffer_UP)
    return True
#end 
def analyzeSPBuyer(planId, planName, writer):
    #print('  Get Lender Info...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        content_lender = readFromUrl(urlSPBuyerPrefix+str(planId))
        if(content_lender != "null"):break
    #end while
    if(content_lender == "null"):
        print((str(planId)+" content_Buyer Error!"))
        return
        
    #content_lender = readFromUrl(urlFPLenderPrefix+str(planId))
    lenderInfo = json.loads(content_lender)
    
    list_lenders = lenderInfo['data']['jsonList']
    #print len(list_lenders)
    reserveHadpayAmount = 0 #加入金额
    for item in list_lenders:
        m = re.match('(\d+-\d+-\d+)T(\d+\:\d+\:\d+)', item['createTime'])
        aDate = m.group(1)
        aClock = m.group(2)
        aTime = str2Datetime(item['createTime'], '%Y-%m-%dT%H:%M:%S')
        buffer_lender = [planName, planId]
        reserveHadpayAmount += item['amount']
        name = item['nickName'].encode('gbk', 'ignore').decode('gbk')
        if name:
            name = '"'+ name+'"'
        buffer_lender.extend([name, item['userId'], item['amount'], aTime])
        
        for index, item in enumerate(buffer_lender):
            if(isinstance(item, str)):
                item = item.encode('gbk', 'ignore').decode('gbk')
                buffer_lender[index] = item
        writer.writerow(buffer_lender)
    return [len(list_lenders), reserveHadpayAmount]
#end def analyzeUPLender()
#-------------------------------------
def analyzeSPlan(planId, planName):
    #print('  Get Performace...')
    tryCount = 0;
    while(tryCount < 5):
        tryCount += 1
        content_plan = readFromUrl(urlSPPerformancePrefix+str(planId))
        if(content_plan != "null"):break
    #end while
    if(content_plan == "null"):
        print((str(planId)+" content_plan Error!"))
        return
        
    #content_plan = readFromUrl(urlFPPerformancePrefix+str(planId))
    planInfo = json.loads(content_plan)
    item = planInfo['data']['autoInvestPlanVos'][0]
    #print item
    #currentDate = getTime('%Y-%m-%d')
    #currentClock = getTime('%H:%M:%S')
    buffer_performance = []
    #reserveDateFormat = time.strptime(item['reserveDate'],u'%Y年%m月%d日')
    #reserveDate = time.strftime('%Y-%m-%d', reserveDateFormat)
    buffer_performance.extend([item['useTime'], item['bidCount'], item['earnInterest'], item['averageBidInterest'], item['borrowCount']])
    #writer.writerow(buffer_performance)
    return buffer_performance
#end def analyzePlan()