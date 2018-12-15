##!/usr/bin/python3
# -*- coding: UTF-8 -*-
# @Author : yutong.han
# @Description : face_keypoint
# @Time: 2018/12/14

import json
import numpy as np
import glob
import matplotlib.pyplot as plt
import os

json_list = glob.glob('C:/Users/yutong.han/Desktop/carnet_realtest_20181129_v20181213_2/carnet_realtest_20181129_v20181213_2/*.json')
#json_list = glob.glob('C:/Users/yutong.han/Desktop/v20181205-lightside_njsmoke_20181102/*.json')
# 存储所有json中所有行的距离lst
key_lst = []
scatter_lst = []
for json_ in json_list:
    json_file = open(json_, 'r').readlines()
    # 存储当前json中所有行的距离lst
    json_lst = []
    for line in json_file:
        # 存储当前json当前行所有点的距离lst
        line_lst = []
        json_dict = json.loads(line)
        #print(json_dict.keys())

        if 'face_keypoint_39' not in json_dict.keys():
            continue

        key = json_dict['face_keypoint_39'][0]['data']
        key_centre = np.array(key[20])
        for i in range(len(key)):
            key_point = np.array(key[i])
            dist = np.linalg.norm(key_centre-key_point)
            # 把所有关键点距离中心的距离存储进line_lst
            line_lst.append(dist)
            scatter_lst.append(dist)
        # 把该行的line_lst存储进json_lst
        json_lst.append(line_lst)
    # 把当前json的所有距离lst存储进key_lst
    key_lst.append(json_lst)
#print(scatter_lst)

max_dis = max(scatter_lst)
#print(max_dis)
min_dis = min(scatter_lst)
#print(min_dis)

plt.hist(np.array(scatter_lst), bins=150, normed=0, facecolor="blue", edgecolor="black", alpha=0.7)
plt.xlabel("L2 Distance")
plt.ylabel("Count")
plt.title("carnet_realtest_20181129")
plt.show()




