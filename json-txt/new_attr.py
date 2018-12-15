'''数据粒度分布处理单个json'''
# -*- coding:utf-8 -*-

import os, sys
import glob
import json
import codecs
import numpy as np


def get_smoke_phone_infos(dataset_json_dir, save_info_name):

    save_file = codecs.open(save_info_name, "w", "utf-8")
    save_file.close()

    #加入所需统计属性（英文及相应中文）
    save_file = codecs.open(save_info_name, "a+", 'utf-8')
    write_line = 'id image_num smoke_nohand smoke_hand smoke_hard nosmoke_bg nosmoke_face nosmoke_susp nosmoke_cover'
    write_line += ' nohand ignore_hand phone_normal phone_backhand phone_hard nophone_face nophone_susp nophone_bg'
    write_line += ' head_count head_avg ' \
                  'head_ignore_no_count  ' \
                  'head_ignore_yes_count ' \
                  'right_eye_closed_count right_eye_open_count right_eye_uncertain_count right_eye_unknown_count ' \
                  'left_eye_closed_count left_eye_open_count left_eye_uncertain_count left_eye_unknown_count ' \
                  'glasses_count sunglasses_count glasses_unknown_count glasses_none_count ' \
                  'hand_count hand_avg hand_ignore_no_count hand_ignore_yes_count'
    write_line+=' face_keypoint_28_count ' \
                'face_keypoint_29_count ' \
               'face_keypoint_39_count ' \
                'face_keypoint_72_count'
    write_line+=' point_attrs_visible point_attrs_invisible point_attrs_occluded keypoint_var\n'
    write_line+='json名称 图片数量总和 抽烟-嘴叼烟没有手数 抽烟-手持且放嘴上数 抽烟-难以分辨数 不抽烟-手在背景区域数 不抽烟-手在人脸附近数 不抽烟-手在嘴巴附近数 不抽烟-严重遮挡数'
    write_line+=' 原始电话数据量 忽略数 拿手机正手打电话数 拿手机反手打电话数 肉眼难以识别打电话数 不拿手机的手在人脸附近数 不拿手机的手在耳朵附近数 不拿手机的手在背景区域数'
    write_line+=' 头数 平均头数 不忽略头数 忽略头数 闭右眼数 睁右眼数 不确定右眼是否睁闭数 不知道右眼是否睁闭数 闭左眼数 睁左眼数 不确定左眼是否睁闭数 不知道左眼是否睁闭数 ' \
                '正常眼镜数 太阳眼镜数 不知道有没有戴眼镜数 不带眼镜数 ' \
                '手数 平均手数 不忽略手数 忽略手数'
    write_line+=' 28点人脸记数 29点人脸记数 39点人脸记数 72点人脸记数'
    write_line+=' 人脸点可见数 人脸点不可见数 人脸点被遮挡数 方差\n'
    save_file.write(write_line)

    #遍历json的每一行
    for json_file_name in glob.glob(dataset_json_dir + '/*.json'):
        json_file = open(json_file_name, 'r')
        base_file_id = os.path.basename(json_file_name)[:-5]
        print(base_file_id, '.json')

        image_num = 0
        # smoke
        smoke_hand_num, smoke_nohand_num, smoke_hard_num = 0, 0, 0
        nosmoke_bg_num, nosmoke_face_num, nosmoke_susp_num, nosmoke_cover_num = 0, 0, 0, 0
        # phone
        nohand_num, ignore_hand_num = 0, 0
        phone_normal_num, phone_backhand_num, phone_hard_num = 0, 0, 0
        nophone_bg_num, nophone_face_num, nophone_susp_num = 0, 0, 0
        # head& eye& glasses& hand
        head_count, head_avg, head_ignore_no_count, head_ignore_yes_count = 0, 0, 0, 0
        right_eye_closed_count, right_eye_open_count, right_eye_uncertain_count, right_eye_unknown_count = 0, 0, 0, 0
        left_eye_closed_count, left_eye_open_count, left_eye_uncertain_count, left_eye_unknown_count = 0, 0, 0, 0
        glasses_count, sunglasses_count, glasses_unknown_count, glasses_none_count = 0, 0, 0, 0
        hand_count, hand_avg, hand_ignore_no_count, hand_ignore_yes_count = 0, 0, 0, 0
        # count
        face_keypoint_28_count, face_keypoint_29_count, face_keypoint_39_count, face_keypoint_72_count = 0, 0, 0, 0
        point_attrs_visible, point_attrs_invisible, point_attrs_occluded , keypoint= 0, 0, 0, (0,0)
        json_lines = json_file.read().splitlines()
        for line in json_lines:
            if line[0] == '#':
                continue
            js = json.loads(line)
            imgName = js["image_key"]
            image_num += 1

            #烟属性统计smoke
            if 'common_box' in js:
                for idx in range(len(js['common_box'])):
                    if js['common_box'][idx]['attrs']['type'] != 'smoke_region':
                        continue

                    select_class = js['common_box'][idx]['attrs']['class']
                    if select_class == 'smoke_hand':
                        smoke_hand_num += 1
                    elif select_class == 'smoke_nohand':
                        smoke_nohand_num += 1
                    elif select_class == 'smoke_hard':
                        smoke_hard_num += 1
                    elif select_class == 'nosmoke_bg':
                        nosmoke_bg_num += 1
                    elif select_class == 'nosmoke_face':
                        nosmoke_face_num += 1
                    elif select_class == 'nosmoke_susp':
                        nosmoke_susp_num += 1
                    elif select_class == 'nosmoke_cover':
                        nosmoke_cover_num += 1
                    else:
                        print('Smoke region not defined', base_file_id, imgName)

            #电话属性统计phone
            if not 'hand' in js:
                nohand_num += 1
            else:
                for idx in range(len(js['hand'])):
                    if 'ignore' in js['hand'][idx]['attrs'].keys():
                        if js['hand'][idx]['attrs']['ignore'] == 'yes':
                            ignore_hand_num += 1
                            continue

                    if 'phone_status' in js['hand'][idx]['attrs'].keys():
                        phone_status = js['hand'][idx]['attrs']['phone_status']
                        if phone_status == 'nophone_bg':
                            nophone_bg_num += 1
                        elif phone_status == 'nophone_face':
                            nophone_face_num += 1
                        elif phone_status == 'nophone_susp':
                            nophone_susp_num += 1
                        elif phone_status == 'phone_normal':
                            phone_normal_num += 1
                        elif phone_status == 'phone_backhand':
                            phone_backhand_num += 1
                        elif phone_status == 'phone_hard':
                            phone_hard_num += 1
                        else:
                            print('Phone status not defined', base_file_id, imgName)

            #头框属性统计（包括头，眼睛（左眼 右眼），眼镜框数的统计）
            if 'head' in js.keys():
                head_count += len(js['head'])
                head_avg = + head_count / image_num
                for idx in range(len(js['head'])):
                    if 'ignore' in js['head'][idx]['attrs'].keys():
                        if js['head'][idx]['attrs']['ignore'] == 'no':
                            head_ignore_no_count += 1
                        else:
                            head_ignore_yes_count += 1
                    if 'right_eye' in js['head'][idx]['attrs'].keys():
                        if js['head'][idx]['attrs']['right_eye'] == 'closed':
                            right_eye_closed_count += 1
                        elif js['head'][idx]['attrs']['right_eye'] == 'open':
                            right_eye_open_count += 1
                        elif js['head'][idx]['attrs']['right_eye'] == 'uncertain':
                            right_eye_uncertain_count += 1
                        else:
                            right_eye_unknown_count += 1
                    if 'left_eye' in js['head'][idx]['attrs'].keys():
                        if js['head'][idx]['attrs']['left_eye'] == 'closed':
                            left_eye_closed_count += 1
                        elif js['head'][idx]['attrs']['left_eye'] == 'open':
                            left_eye_open_count += 1
                        elif js['head'][idx]['attrs']['left_eye'] == 'uncertain':
                            left_eye_uncertain_count += 1
                        else:
                            left_eye_unknown_count += 1
                    if 'has_glasses' in js['head'][idx]['attrs'].keys():
                        if js['head'][idx]['attrs']['has_glasses'] == 'glasses':
                            glasses_count += 1
                        elif js['head'][idx]['attrs']['has_glasses'] == 'sunglasses':
                            sunglasses_count += 1
                        elif js['head'][idx]['attrs']['has_glasses'] == 'unknown':
                            glasses_unknown_count += 1
                        else:
                            glasses_none_count += 1

            #手框属性的统计
            if 'hand' in js.keys():
                hand_count += len(js['hand'])
                hand_avg += hand_count / image_num
                for idx in range(len(js['hand'])):
                    if 'ignore' in js['hand'][idx]['attrs']:
                        if js['hand'][idx]['attrs']['ignore'] == 'no':
                            hand_ignore_no_count += 1
                        else:
                            hand_ignore_no_count += 1

            #人脸框关键点属性统计face_keypoint
            key_lst=[]
            if 'face_keypoint_28' in js.keys():
                face_keypoint_28_count += 1
                point_attrs_visible += js['face_keypoint_28'][0]['point_attrs'].count('full_visible')
                point_attrs_invisible += js['face_keypoint_28'][0]['point_attrs'].count('invisible')
                point_attrs_occluded += js['face_keypoint_28'][0]['point_attrs'].count('occluded')
                key = js['face_keypoint_28'][0]['data']
                key = np.var(key, axis=0)
                key_lst.append(list(key))

            if 'face_keypoint_29' in js.keys():
                face_keypoint_29_count += 1
                point_attrs_visible += js['face_keypoint_29'][0]['point_attrs'].count('full_visible')
                point_attrs_invisible += js['face_keypoint_29'][0]['point_attrs'].count('invisible')
                point_attrs_occluded += js['face_keypoint_29'][0]['point_attrs'].count('occluded')
                key = js['face_keypoint_29'][0]['data']
                key = np.var(key, axis=0)
                key_lst.append(list(key))

            if 'face_keypoint_39' in js.keys():
                face_keypoint_39_count += 1
                point_attrs_visible += js['face_keypoint_39'][0]['point_attrs'].count('full_visible')
                point_attrs_invisible += js['face_keypoint_39'][0]['point_attrs'].count('invisible')
                point_attrs_occluded += js['face_keypoint_39'][0]['point_attrs'].count('occluded')
                key = js['face_keypoint_38'][0]['data']
                key = np.var(key, axis=0)
                key_lst.append(list(key))

            if 'face_keypoint_72' in js.keys():
                face_keypoint_72_count += 1
                point_attrs_visible += js['face_keypoint_72'][0]['point_attrs'].count('full_visible')
                point_attrs_invisible += js['face_keypoint_72'][0]['point_attrs'].count('invisible')
                point_attrs_occluded += js['face_keypoint_72'][0]['point_attrs'].count('occluded')
                key = js['face_keypoint_72'][0]['data']
                key = np.var(key, axis=0)
                key_lst.append(list(key))

            keypoint = np.mean(key_lst, axis=0)
            min=np.min(keypoint,axis=0)
            print(min)
            keypoint = tuple(keypoint)
            #print(keypoint)



        # end of all lines

        #写入txt文件
        write_line = base_file_id + ' %d' % (image_num)
        write_line += ' %d %d %d %d %d %d %d' % (
            smoke_nohand_num, smoke_hand_num, smoke_hard_num, nosmoke_bg_num, nosmoke_face_num, nosmoke_susp_num,
            nosmoke_cover_num)
        write_line += ' %d %d %d %d %d %d %d %d' % (
            nohand_num, ignore_hand_num, phone_normal_num, phone_backhand_num, phone_hard_num, nophone_face_num,
            nophone_susp_num, nophone_bg_num)
        write_line += ' %d %d %d %d' % (head_count, head_avg, head_ignore_no_count, head_ignore_yes_count)
        write_line += ' %d %d %d %d' % (
        right_eye_closed_count, right_eye_open_count, right_eye_uncertain_count, right_eye_unknown_count)
        write_line += ' %d %d %d %d' % (
        left_eye_closed_count, left_eye_open_count, left_eye_uncertain_count, left_eye_unknown_count)
        write_line += ' %d %d %d %d' % (glasses_count, sunglasses_count, glasses_unknown_count, glasses_none_count)
        write_line += ' %d %d %d %d' % (hand_count, hand_avg, hand_ignore_no_count, hand_ignore_yes_count)
        write_line += ' %d %d %d %d %d %d %d %s\n' % (
        face_keypoint_28_count, face_keypoint_29_count, face_keypoint_39_count, face_keypoint_72_count,
        point_attrs_visible, point_attrs_invisible, point_attrs_occluded, keypoint)

        save_file.write(write_line)
        json_file.close()
    save_file.close()
    print('write done', save_info_name)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('get_smoke_phone_infos.py dataset_json_dir save_info_name')
        exit()
    dataset_json_dir = sys.argv[1]
    save_info_name = sys.argv[2]
    get_smoke_phone_infos(dataset_json_dir, save_info_name)





