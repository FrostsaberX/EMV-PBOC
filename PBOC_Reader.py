#!/usr/bin/python
# -*- coding: UTF-8 -*-
import re
import subprocess, os, binascii
from bankcode import *

def getCardType(cardnumber):
    for len in range(5, 9):
        if bankcode.has_key(cardnumber[0:len]):
            return bankcode[cardnumber[0:len]]
    return ''

def getHistory(historystr,number):
    if len(historystr) >= 24:
        time = "20" + historystr[0:2] + "-" + historystr[2:4] + "-" + historystr[4:6] + " " + historystr[6:8] + ":" + historystr[8:10] + ":" + historystr[10:12]
        money = historystr[12:24]
        place = binascii.a2b_hex(historystr[44:84]).decode('gbk')
        return str(number) + "	" + time + "		" + str(float(money)/100) + "			"  + place
    else:
        return ''

os.system("clear")
# 启动Proxmark3,此处自行设置proxmark3客户端所在的路径以及设备名
pm3 = subprocess.Popen("/usr/local/Cellar/proxmark3/4.16717/bin/proxmark3 --flush /dev/tty.usbmodemiceman1", shell=True, stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)

# 随便发一串数据，然后不保留场的开启
pm3.stdin.write('hf 14a raw -c 0300B2020C\n')

# 选择支付系统PSE-1PAY.SYS.DDF01,并建立连接
pm3.stdin.write('hf 14a raw -c -s -k 0200A404000E315041592E5359532E4444463031\n')
# 借记卡最后一位为1贷记卡为2
pm3.stdin.write('hf 14a raw -c 0300A4040008A000000333010101 -k\n')
# 发送银行卡信息查询命令
pm3.stdin.write('hf 14a raw -c 0200B2010C -k\n')
# 发送卡主信息查询指令
pm3.stdin.write('hf 14a raw -c 0300B2020C -k\n')

# 循环发送消费记录查询命令
for i in range(1, 11):
    head = '02'
    if i % 2 == 0: head = '03'
    if i != 10: i = "0" + str(i)
    pm3.stdin.write('hf 14a raw -c ' + head + '00B2'+ str(i) +'5C00 -k\n')

# 断开银行卡连接
pm3.stdin.write('hf 14a reader\n')
out = pm3.communicate()[0].decode(encoding="utf-8", errors='ignore')
outarray = out.split("[usb|script] pm3 --> ")

def get_hex_from_line(line):
    line = line.replace(" ", "")
    seaObj = re.search("]([A-F0-9]+)\[", line)
    if seaObj is not None:
        return seaObj.group(1)
    return None

# 0位置输出的是exe的banner
# 1位置是关闭场的之类
# 2位置是选择支付系统
# 3位置是卡类型
# 4位置是卡信息

cardnumber = get_hex_from_line(outarray[4].split('\n')[1])[10:29]

print cardnumber
print outarray

idnumber = get_hex_from_line(outarray[5].split('\n')[1])
history = list()

# 循环添加交易记录到history列表
for i in range(6,16):
    history.append(get_hex_from_line(outarray[i].split('\n')[1])[2:100])

print '----------------------------------------------------------------------------------------'
print '                                   银行闪付卡信息显示                                   '
print '----------------------------------------------------------------------------------------'
#if len(idnumber) >= 90:
print u'姓      名：' + binascii.a2b_hex(idnumber[60:-8]).decode('gbk')
print u'卡主身份证：' + binascii.a2b_hex(idnumber[12:48]).decode('gbk')

print u'银行卡卡号：' + cardnumber
print u'银行卡类型：' + getCardType(cardnumber)
print '----------------------------------------------------------------------------------------'
print u'编号	交易时间			交易金额		交易地点'
for i in range(len(history)):
    print '----------------------------------------------------------------------------------------'
    print getHistory(history[i],i+1)
# 删除proxmark3的运行日志
os.system("rm proxmark3.log")
# 删除proxmark3的历史记录
os.system("rm .history")
