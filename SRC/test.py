# -*- coding: utf-8 -*-

import json

datastring = u'{"status":0,"data":{"creditInfo":{"creditInfoId":417273,"user":421930}, "loan":{"loanId":100000,"title":"买车"}}}'
datastring2 = u'{"status":0,"data":{"creditInfo":{"creditInfoId":632061,"user":636942,"identificationScanning":"VALID","mobile":"INVALID","graduation":"INVALID","credit":"VALID","residence":"INVALID","marriage":"INVALID","child":"INVALID","album":"INVALID","work":"VALID","renren":"INVALID","kaixin":"INVALID","house":"INVALID","car":"INVALID","identification":"VALID","detailInformation":"INVALID","borrowStudy":"VALID","mobileReceipt":"INVALID","incomeDuty":"VALID","other":"INVALID","account":"INVALID","titles":"INVALID","fieldAudit":"INVALID","mobileAuth":"INVALID","video":"INVALID","version":0},"creditPassedTime":{"creditPassedTimeId":632025,"user":636942,"credit":"Feb 28, 2014 6:32:57 PM","work":"Feb 28, 2014 6:32:57 PM","incomeDuty":"Feb 28, 2014 6:32:57 PM","identificationScanning":"Feb 28, 2014 6:32:57 PM","identification":"Feb 28, 2014 6:32:57 PM"},"loan":{"loanId":168675,"title":"装修办公场所","borrowType":"其他借款","picture":"../images/loanType/other.png","amount":93400.0,"interest":13.2,"months":36,"description":"客户此次借款主要用于装修办公场所。客户是重庆渝中区人，自己经营了一家医疗器械的公司，每月有稳定的流水。 上述信息已经实地认证方友众信业公司考察认证。同时，经审核借款人所提供资料真实有效，符合人人贷的借款审核标准。","loanType":"DEBX","productName":"友信","repayType":"MONTH","status":"FIRST_READY","verifyState":"WAITING_INVESTIGATION","allowAccess":true,"utmSource":"debx-yx","openTime":"Feb 28, 2014 6:32:57 PM","startTime":"Mar 7, 2014 6:32:57 PM","readyTime":"Feb 28, 2014 6:33:23 PM","surplusAmount":0.0,"finishedRatio":100.0,"repaidByGuarantor":false,"monthlyMinInterest":"[{\"month\":\"12\",\"minInterest\":\"12\",\"maxInterest\":\"12\",\"mgmtFee\":\"0\",\"tradeFee\":\"0\",\"guaranteeFee\":\"2\",\"inRepayPenalFee\":\"0\",\"divideFee\":40.0},{\"month\":\"18\",\"minInterest\":\"12.0\",\"maxInterest\":\"12\",\"mgmtFee\":\"0\",\"tradeFee\":\"0\",\"guaranteeFee\":\"2\",\"inRepayPenalFee\":\"0\",\"divideFee\":40.0},{\"month\":\"24\",\"minInterest\":\"12.5\",\"maxInterest\":\"13.2\",\"mgmtFee\":\"0\",\"tradeFee\":\"0\",\"guaranteeFee\":\"2\",\"inRepayPenalFee\":\"0\",\"divideFee\":40.0},{\"month\":\"36\",\"minInterest\":\"13.2\",\"maxInterest\":\"13.2\",\"mgmtFee\":\"0\",\"tradeFee\":\"0\",\"guaranteeFee\":\"2\",\"inRepayPenalFee\":\"0\",\"divideFee\":40.0}]","borrowerId":636942,"forbidComment":false,"nickName":"ShenP_0618203161.yx","avatar":"","borrowerLevel":"A","address":"重庆","jobType":"私营企业主","displayLoanType":"SDRZ","currentIsRepaid":false,"amountPerShare":50.0,"oldLoan":false,"interestPerShare":0.0,"principal":0.0,"leftMonths":36,"overDued":false,"productId":26}}}'

datastring2 = datastring2.replace('"[', '[').replace(']"', ']')
#print datastring2.encode('gbk')
s = json.loads(datastring2)
print s
print s.keys()
print s['data']['loan']['monthlyMinInterest'][0]
#print(s['data']['loan']['title'].encode('gbk'))

#两种解决方法：原字符串前加r；将[]两边的引号去掉