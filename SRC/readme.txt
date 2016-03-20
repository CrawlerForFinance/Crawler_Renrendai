人人贷抓取程序0326：
1. OrderCrawler为服务器中断导致的网页读取不完整错误将不会再中断线程，而是等待一段时间后继续尝试抓取。
2. 解决OrderCrawler因为强制中断导致的文件并没有写入的问题。

=======================================================
人人贷抓取程序0313：
1. FindLostOrders_renrendai.exe用来查找“rrdai_1标的详情.csv”类型的csv文件中被跳过的loanID。方法：将csv文件集中放在exe当前目录下的文件夹中，根据提示输入文件夹名称，结果保存在“LostOrder_文件夹名称_日期.txt”中，每个loanID占一行。
2. Crawler_renrendai因为服务器中断导致的网页读取不完整错误将不会再中断线程，而是记录在LostOrder日志中。
3. 解决因为csv文件不识别奇怪字符导致的错误。
=======================================================

人人贷抓取程序0310：

1. 程序代码从python2.7升级到了python3.4，对编码乱码解决更好；
2.  Crawler_renrendai程序除原有csv文件外，额外生成一个“LostOrder_日期.txt”记录爬取过程中跳过的loanID。导致跳过的原因可能有多种，并且很难测试完全，如果有遗漏请联系我；
3. “LostOrder_日期.txt”可以通过改名为"orderlist"来使用OrderCrawler_renrendai.exe来爬取；
4. FindLostOrders_renrendai.exe用来查找“rrdai_1标的详情_30000-30010_201503102017.csv”类型的csv文件中被跳过的loanID,将csv文件放在exe当前目录下，根据提示输入csv文件名，结果保存在“LostOrder_rrdai_1标的详情_30000-30010_201503102017.csv.txt”中，每个loanID占一行。PS:对于很久之前格式不同的csv，程序可能会发生异常。
5. “OrderCrawler_renrendai.exe”输出的文件名已经改成“rrdai_1...”的格式；

=======================================================

人人贷抓取程序1231：

说明：
1. config.ini文件中[proxy]内项host和port为代理服务器地址和端口；
2. 程序默认线程数为1，修改线程数可以在执行时添加参数-t [thread number]，也可以修改config.ini文件中threadnumber;
3. 执行时使用参数-s [startID]和-e [endID]可以设置起始/结束序号；
4. 使用-h或--help命令可查看参数使用方法；

5. 若不了解如何使用命令行启动，以上都可以忽略，使用默认参数执行。


程序数据中的一些问题：
UPCrawler抓取的U_plan_**.csv表格中“预定开始时间”等几项格式为“月/日 时:分”，没有“年”，但用excel打开时显示会自动补全当前年份，实际数据中（用文本格式打开）是没有“年”的。