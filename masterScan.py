#!/usr/bin/python3
# -*- coding: utf-8  -*-
import os,queue,time
import re
import argparse
import logging
import multiprocessing
from operator import itemgetter, attrgetter
from multiprocessing.managers import BaseManager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

logbegin = time.time()

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

#ignlist = []
dictCount = {}
question = 0
resultCount = 0
fileCount = 0
args_u = ''
args_at = ''
args_bt = ''

sourceDir = '/wls/aodi/acclog/acclogprd'
#sourceDir = 'D:\WSpcap\\acclog'
reString = re.compile(r'^access.log.\d{8}$')
task_queue = queue.Queue()
result_queue = queue.Queue()
question_queue = queue.Queue()
args_U_queue = queue.Queue()
args_bt_queue = queue.Queue()
args_at_queue = queue.Queue()
class QueueManager(BaseManager):
    pass

QueueManager.register('get_task_queue', callable=lambda: task_queue)
QueueManager.register('get_result_queue', callable=lambda: result_queue)
QueueManager.register('get_question_queue', callable=lambda: question_queue)
QueueManager.register('get_args_U_queue', callable=lambda: args_U_queue)
QueueManager.register('get_args_bt_queue', callable=lambda: args_bt_queue)
QueueManager.register('get_args_at_queue', callable=lambda: args_at_queue)
m = QueueManager(address=('127.0.0.1', 5000), authkey=b'abc')

m.start()
task_queue = m.get_task_queue()
result_queue = m.get_result_queue()
question_queue = m.get_question_queue()
args_U_queue = m.get_args_U_queue()
args_bt_queue = m.get_args_bt_queue()
args_at_queue = m.get_args_at_queue()
def run():
    global question
    global args_u
    global args_at
    global args_bt
    if args.s == 'all' and args.n == 'all':
        question = 1
        question_queue.put(question)
    if args.i == 'all' and args.n:
        question = 2
        question_queue.put(question)
    if args.bt and args.at and args.U:
        question = 3
        question_queue.put(question)
        args_u = args.U
        args_U_queue.put(args_u)
        args_at = args.at
        args_at_queue.put(args_at)
        args_bt = args.bt
        args_bt_queue.put(args_bt)
    if args.U and args.n:
        question = 4
        question_queue.put(question)
        args_u = args.U
        args_U_queue.put(args_u)
    if args.U and args.lt and args.st and args.avt:
        question = 5
        question_queue.put(question)
        args_u = args.U
        args_U_queue.put(args_u)
    if question not in (1, 2, 3, 4, 5):
        print("请按照题目要求输入参数")

def start():
    global resultCount
    global fileCount
    #global taskFlag
    #checkthread().start()
    run()
    for root, dirs, files in os.walk(sourceDir):
        # for files in os.listdir(source_dir):
        for fn in files:
            fileCount = fileCount + 1
            r = reString.match(fn)
            if r is not None:
                #if fn not in ignlist:
                    #ignlist.append(fn)
                sfile = os.path.join(root, fn)  # sfile文件绝对路径
                task_queue.put(sfile)
    # while result_queue.qsize()>0:
    while True:
        if result_queue.qsize()>0:
            print('task_queue size is {0}'.format(task_queue.qsize()))
            result = result_queue.get()
            resultCount = resultCount + 1
            #print(result)
            for i, j in result.items():
                if i not in dictCount:
                    dictCount[i] = j
                else:
                    dictCount[i] = dictCount[i] + j
            #print(dictCount)
            if resultCount == fileCount and question in (1, 3):
                print(sorted(dictCount.items(), key=itemgetter(1), reverse=True))
                logend = time.time()
                print('cost {0} '.format(logend-logbegin))
                break
            if resultCount == fileCount and question == 2:
                if args.n != "all":
                    print(sorted(dictCount.items(), key=itemgetter(1), reverse=True)[:int(args.n)])
                    logend = time.time()
                    print('cost {0} '.format(logend - logbegin))
                    break
                elif args.n == "all":
                    print(sorted(dictCount.items(), key=itemgetter(1), reverse=True))
                    logend = time.time()
                    print('cost {0} '.format(logend - logbegin))
                    break
            if resultCount == fileCount and question == 4:
                j = ()
                listSort = []
                if args.n != "all":
                    a = sorted(dictCount.items(), key=itemgetter(1), reverse=True)[:int(args.n)]
                    for i in a:
                        j = (i[1], args_u, i[0])
                        listSort.append(j)
                    print(listSort)
                    logend = time.time()
                    print('cost {0} '.format(logend - logbegin))
                    break
                elif args.n == "all":
                    a = sorted(dictCount.items(), key=itemgetter(1), reverse=True)
                    for i in a:
                        j = (i[1], args_u, i[0])
                        listSort.append(j)
                    print(listSort)
                    logend = time.time()
                    print('cost {0} '.format(logend - logbegin))
                    break
            if resultCount == fileCount and question == 5:
                a = sorted(dictCount.items(), key=lambda d: int(d[0]), reverse=True)
                ltime = a[0][0]
                stime = a[-1][0]
                avtimes = 0
                sum = 0
                aaa = 0
                for key, value in dictCount.items():
                    sum = sum + int(key) * value
                    avtimes = avtimes + value
                    aaa = aaa + value
                avtime = sum / avtimes
                print("{0} {1}ms {2}ms {3:.2f}ms {4}".format(args.U, ltime, stime, avtime, aaa))
                logend = time.time()
                print('cost {0} '.format(logend - logbegin))

#class checkthread(multiprocessing.Process):
#    def run(self):
#        global resultCount
#        global fileCount
#        global taskFlag
#        logger.info("checkthread start")
#        while True:
#            print("{0}{1}".format(result_queue.qsize(),resultCount))
#            time.sleep(1)
#            if task_queue.qsize() == 0 and resultCount == 9:
#                print(sorted(dictCount.items(), key=itemgetter(1), reverse=True))
#                logend = time.time()
#                print('cost {0} '.format(logend-logbegin))
#                taskFlag = False
#                print(taskFlag)
#                break
#            else:
#                pass



start()
