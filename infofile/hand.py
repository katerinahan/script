#  -*- coding:utf-8 -*-
# !/usr/bin/env python

import os
import sys

if __name__ == "__main__":

  path = input("请输入目标路径:")
  arg = input("请输入1.清洗; 2.撤回:")
  if path[-1] == '/':
    path = path[:len(path)-1]
  
  dirs = os.listdir(path) # ['pts72_refresh_plus_201807', 'tianjin201806']
  #dirs.remove('.DS_Store')

  for dir in dirs:
    dir_path = path + '/' + dir
    sub_dirs = os.listdir(dir_path) # ['5855', '5873']
    
    for sub_dir in sub_dirs:
      sub_dir_path = dir_path + '/' + sub_dir
      sub_sub_dirs = os.listdir(sub_dir_path) # ['hand', 'nohand'] or ['nohand'] etc.
      
      for hand_type in sub_sub_dirs:
        if int(arg) == 1:
            if hand_type == 'hand':
              os.makedirs(sub_dir_path + '/' + hand_type + '/ignore')
              os.makedirs(sub_dir_path + '/' + hand_type + '/correct')
              os.makedirs(sub_dir_path + '/' + hand_type + '/incorrect')
            else:
              os.makedirs(sub_dir_path + '/' + hand_type + '/normal')
              os.makedirs(sub_dir_path + '/' + hand_type + '/ignore')
        elif int(arg) == 2:
            if hand_type == 'hand':
              os.rmdir(sub_dir_path + '/' + hand_type + '/ignore')
              os.rmdir(sub_dir_path + '/' + hand_type + '/correct')
              os.rmdir(sub_dir_path + '/' + hand_type + '/incorrect')
            else:
              os.rmdir(sub_dir_path + '/' + hand_type + '/normal')
              os.rmdir(sub_dir_path + '/' + hand_type + '/ignore')
        else:
              print("非法输入，输入仅可为1或2")
              break