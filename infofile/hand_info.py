#  -*- coding:utf-8 -*-
# !/usr/bin/env python

import os
import sys

if __name__ == "__main__":

    # if (len(sys.argv) < 2):
    #     print ("please input one argument")
    #     os.system("pause")

    path = input("请输入目标路径：")  # 新建文件夹的路径
    arg = input("请输入1（清洗）、2（撤回）：")
    # print(path)
    i = 0
    # all = input("请输入需要新建多少个文件夹：")
    all = 3
    hand = {'0': 'left_hand', '1': 'right_hand', '2':'ignore'};

    while i < all:  # 新建3个文件夹
        # print(i)
        for each_dir in os.listdir(path):
            # print(each_dir)

            if int(arg) == 1:
                file_name = path + '\\' + each_dir + '\\' + hand[str(i)]  # 字典的值为新建文件夹的命名
                # print(file_name)
                os.makedirs(file_name)

            elif int(arg) == 2:
                file_name = path + '\\' + each_dir + '\\' + hand[str(i)]  # 字典的值为新建文件夹的命名
                # print(file_name)
                os.rmdir(file_name)

            elif int(arg) == 3:
                file_name = path + '\\' + each_dir + '\\' + hand[str(i)]  # 字典的值为新建文件夹的命名
                # print(file_name)
                os.rmdir(file_name)

            # print( each_dir, ' ',i ,' ',file_name)

            if int(arg) < 3:
                print(file_name + "  创建成功！")
            else:
                print(file_name + "  删除成功！")
            # os.mkdir(file_name)

        i = i + 1