#!/usr/bin/python3
# -*- coding: utf-8  -*-
import time
import re, os, queue
import logging
import argparse
from datetime import datetime
from operator import itemgetter, attrgetter
from multiprocessing.managers import BaseManager

task_queue = queue.Queue()
result_queue = queue.Queue()
question_queue = queue.Queue()
args_U_queue = queue.Queue()
args_bt_queue = queue.Queue()
args_at_queue = queue.Queue()
class QueueManager(BaseManager):
    pass
QueueManager.register('get_task_queue')
QueueManager.register('get_result_queue')
QueueManager.register('get_question_queue')
QueueManager.register('get_args_U_queue')
QueueManager.register('get_args_bt_queue')
QueueManager.register('get_args_at_queue')
m = QueueManager(address=('127.0.0.1', 5000), authkey=b'abc')
m.connect()
task_queue = m.get_task_queue()
result_queue = m.get_result_queue()
question_queue = m.get_question_queue()
args_U_queue = m.get_args_U_queue()
args_bt_queue = m.get_args_bt_queue()
args_at_queue = m.get_args_at_queue()

parser = argparse.ArgumentParser()
parser.add_argument("-at", help="after time")
parser.add_argument("-bt", help="before time")
parser.add_argument("-U", help="resource")
parser.add_argument("-n", help="disPlay number")
parser.add_argument("-i", help="IP")
parser.add_argument("-s", help="status code")
parser.add_argument("-lt", action="store_true", help="long time")
parser.add_argument("-st", action="store_true", help="short time")
parser.add_argument("-avt", action="store_true", help="average time")
args = parser.parse_args()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

# sourceDir = conf.get('source','dir')
#sourceDir = '/wls/aodi/acclog/acclogprd'
# reString = conf.get('Scan_file_Formatter','acclog')
#reString = re.compile(r'^access.log.\d{8}$')
dictCount = {}
logbegin = time.time()
question = 0
args_u = 0
args_at = 0
args_bt = 0


class anaLog():
    def __init__(self, file):
        self.file = file
        self.request_list = []
        self.__message = ''
        self.filename = os.path.basename(self.file)

    def anaLogStatus(self):
        re_keywords_status = re.compile(r'.*HTTP/1.1" (\d{3}).*ms')
        with open(self.file, 'rb') as f:
            while True:
                line = f.readline()
                __message = str(line)
                if line == b'':
                    break
                a = re_keywords_status.match(__message)
                if a:
                    line_status = a.group(1)
                    self.request_list.append([line_status])

    def anaLogIp(self):
        global args
        re_keywords_Ip = re.compile(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).+\d+ms$')
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i in lines:
                __message = i.rstrip('\n')
                if i == b'':
                    break
                a = re_keywords_Ip.match(__message)
                if a:
                    line_Ip = a.group(1)
                    self.request_list.append([line_Ip])

    def anaLogResource(self):
        global args
        re_keywords_Ip = re.compile(r'(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}).*' + args_u + '.+\d+ms')
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i in lines:
                __message = i.rstrip('\n')
                if i == b'':
                    break
                a = re_keywords_Ip.search(__message)
                if a:
                    line_time_strp = datetime.strptime(a.group(1), "%d/%b/%Y:%H:%M:%S")
                    if line_time_strp > datetime.strptime(args_at,"%Y%m%d%H%M%S") and line_time_strp < datetime.strptime(args_bt, "%Y%m%d%H%M%S"):
                        # line_time = line_time_strp.strftime('%Y%m%d%H%M%S')
                        self.request_list.append([args_u])
                    else:
                        pass

    def anaLogResourceTimes(self):
        re_keywords_Ip = re.compile(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}).*' + args_u + '.+\d+ms$')
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i in lines:
                __message = i.rstrip('\n')
                a = re_keywords_Ip.match(__message)
                if a:
                    line_Ip = a.group(1)
                    self.request_list.append([line_Ip])
                else:
                    pass

    def anaLogRsponseTimes(self):
        re_keywords_Ip = re.compile(r'.*' + args_u + '.*\s(\d+)ms')
        with open(self.file, 'r') as f:
            lines = f.readlines()
            for i in lines:
                __message = i.rstrip('\n')
                a = re_keywords_Ip.match(__message)
                if a:
                    line_Response = a.group(1)
                    self.request_list.append([line_Response])
                else:
                    pass

    def anaTimes(self):
        number = 0
        for i in self.request_list:
            if i[0] not in dictCount:
                dictCount[i[0]] = number
            dictCount[i[0]] = dictCount[i[0]] + 1
        self.request_list = []

    def DictResourceTimes(self):
        for i in self.request_list:
            if i[0] not in dictCount:
                dictCount[i[0]] = [args.U, 0]
            dictCount[i[0]][1] = dictCount[i[0]][1] + 1


def run():
    global question
    global dictCount
    global args_u
    global args_bt
    global args_at
    question = question_queue.get()
    question_queue.put(question)
    if args_U_queue.qsize()>0:
        args_u = args_U_queue.get()
        args_U_queue.put(args_u)
    if args_bt_queue.qsize()>0:
        args_bt = args_bt_queue.get()
        args_bt_queue.put(args_bt)
    if args_at_queue.qsize()>0:
        args_at = args_at_queue.get()
        args_at_queue.put(args_at)
    while task_queue.qsize()>0:
        print('task_queue size is {0}'.format(task_queue.qsize()))
        fn = task_queue.get()
        if question == 1:
            aa = anaLog(fn)
            aa.anaLogStatus()
            aa.anaTimes()
            result_queue.put(dictCount)
            dictCount = {}
        if question == 2:
            aa = anaLog(fn)
            aa.anaLogIp()
            aa.anaTimes()
            result_queue.put(dictCount)
            #print(dictCount)
            dictCount = {}
        if question == 3:
            aa = anaLog(fn)
            aa.anaLogResource()
            aa.anaTimes()
            result_queue.put(dictCount)
            dictCount = {}
        if question == 4:
            aa = anaLog(fn)
            aa.anaLogResourceTimes()
            aa.anaTimes()
            result_queue.put(dictCount)
            dictCount = {}
        if question == 5:
            aa = anaLog(fn)
            aa.anaLogRsponseTimes()
            aa.anaTimes()
            result_queue.put(dictCount)
            dictCount = {}

    #if question in (1, 3):
    #    print(sorted(dictCount.items(), key=itemgetter(1), reverse=True))
    #    logend = time.time()
    #    print('cost {0} '.format(logend - logbegin))
    #if question in (2, 4):
    #    if args.n != "all":
    #        print(sorted(dictCount.items(), key=itemgetter(1), reverse=True)[:int(args.n)])
    #        logend = time.time()
    #        print('cost {0} '.format(logend - logbegin))
    #    elif args.n == "all":
    #        print(sorted(dictCount.items(), key=itemgetter(1), reverse=True))
    #        logend = time.time()
    #        print('cost {0} '.format(logend - logbegin))
    #if question == 5:
    #    a = sorted(dictCount.items(), key=lambda d: int(d[0]), reverse=True)
    #    ltime = a[0][0]
    #    stime = a[-1][0]
    #    avtimes = 0
    #    sum = 0
    #    aaa = 0
    #    for key, value in dictCount.items():
    #        sum = sum + int(key) * value
    #        avtimes = avtimes + value
    #        aaa = aaa + value
    #    avtime = sum / avtimes
    #    print("{0} {1}ms {2}ms {3:.2f}ms {4}".format(args.U, ltime, stime, avtime, aaa))
    #    logend = time.time()
    #    print('cost {0} '.format(logend - logbegin))


if __name__ == "__main__":
    run()
# print(sorted(dictCount.items(), key=lambda d:d[0],reverse=True))
# a = sorted(dictCount.items(), key=lambda d:int(d[0]),reverse=True)
# print(a)
