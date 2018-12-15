import os,shutil
import sys
#-*- coding:utf-8 -*-

root = input("请输入需要进行统计的路径： ")
suffix = input("请按照“.***”的格式输入需要进行统计的文件类型： ")
ofname = input("请按照“***\count.csv”的格式输入统计结果存放路径：")

fout=open(ofname, 'w')
delimiter = '/' if sys.platform == 'darwin' or 'linux' in sys.platform else '\\'

data = {}
counter = 0

for root, subdirs, files in os.walk(root):
    for ff in files:
        if ff.endswith(suffix):
            counter += 1
            path = os.path.join(root, ff)

            date = path.split(delimiter)[-2]

            if date not in data:
                print(date)
                data[date] = []

            data[date].append(ff)

            if counter % 50000 == 0:
                print('Processed file: ', counter)

for date in data:
    fout.write(date + ',' + str(len(data[date])) + '\n')

    #for ff in data[date]:
    #    fout.write(' ,' + ff + '\n')

fout.close()
