import os
import sys
import glob
import shutil
import dms_json
import dms_utils
import json
import codecs
from collections import OrderedDict

def getPhoneStatus(image_path, data_id, imgName):
  region_class = ['ignore', 'nophone_background', 'nophone_face', 'nophone_suspect', 'phone_normal', 'phone_backhand', 'phone_hard']
  label_class = ['ignore', 'nophone_bg', 'nophone_face', 'nophone_susp', 'phone_normal', 'phone_backhand', 'phone_hard']
  select_class = None
  for class_id in range(len(region_class)):
    cur_class = region_class[class_id]
    cur_label_class = label_class[class_id]
    check_file_name = os.path.join(image_path, data_id, cur_class, imgName)
    if os.path.isfile(check_file_name):
      select_class = cur_label_class
      #print check_file_name
      break
  return select_class

def add_hand_phone_status(org_json_dir, dst_json_dir, done_root_dir):
  if not os.path.exists(dst_json_dir):
    os.makedirs(dst_json_dir)
  
  ignore_hand_num = 0
  phone_normal_num, phone_backhand_num, phone_hard_num = 0, 0, 0
  nophone_bg_num, nophone_face_num, nophone_susp_num = 0, 0, 0
  for json_file_name in glob.glob(org_json_dir + '/*.json'):
    json_file = open(json_file_name, 'r')
    base_file_id = os.path.basename(json_file_name)[:-5]
    print(base_file_id + '.json')
    
    json_lines = json_file.read().splitlines()
    dst_json_lines = []
    
    new_json_file = codecs.open(dst_json_dir + '/' + base_file_id + '.json', "w", "utf-8")
    new_json_file.close()
    new_json_file = codecs.open(dst_json_dir + '/' + base_file_id + '.json', "a+", 'utf-8')
    for line in json_lines:
      if line[0] == '#':
        new_json_file.write(line + '\n')
        continue
      js = json.loads(line, object_pairs_hook=OrderedDict)
      
      #new_js_line = json.dumps(js) + "\n"
      #new_json_file.write(new_js_line)
      #continue
      
      imgName = js["image_key"]
      if not 'hand' in js:
        new_js_line = json.dumps(js) + "\n" # no common box
        new_json_file.write(new_js_line)
        continue
      
      has_hand = False
      if 'hand' in js:
        for hand_id in range(len(js['hand'])):
          has_hand = True
          break
      if has_hand == False:
        new_js_line = json.dumps(js) + "\n" # no hand
        new_json_file.write(new_js_line)
        continue
      
      # change each hand
      if 'hand' in js:
        for box_id in range(len(js['hand'])):
          hand_id = js['hand'][box_id]['id']
          select_class = None
          select_class = getPhoneStatus(done_root_dir, base_file_id, imgName + '_' + str(hand_id) + '.png')
          
          if select_class == 'ignore':
            js['hand'][box_id]['attrs']['ignore'] = 'yes'
            js['hand'][box_id]['attrs']['phone_status'] = 'unknown'
            ignore_hand_num += 1
          elif select_class == 'nophone_bg':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'nophone_bg'
            nophone_bg_num += 1
          elif select_class == 'nophone_face':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'nophone_face'
            nophone_face_num += 1
          elif select_class == 'nophone_susp':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'nophone_susp'
            nophone_susp_num += 1
          elif select_class == 'phone_normal':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'phone_normal'
            phone_normal_num += 1
          elif select_class == 'phone_backhand':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'phone_backhand'
            phone_backhand_num += 1
          elif select_class == 'phone_hard':
            js['hand'][box_id]['attrs']['ignore'] = 'no'
            js['hand'][box_id]['attrs']['phone_status'] = 'phone_hard'
            phone_hard_num += 1
          elif 'ignore' in js['hand'][box_id]['attrs']:
            if js['hand'][box_id]['attrs']['ignore'] == 'yes':
              js['hand'][box_id]['attrs']['ignore'] = 'yes'
              js['hand'][box_id]['attrs']['phone_status'] = 'unknown'
              ignore_hand_num += 1
            else:
              #print('Error class: ', select_class)
              #print(done_root_dir, base_file_id, imgName + '_' + str(hand_id) + '.png')
              continue
          else:
            #print('Error class: ', select_class)
            #print(done_root_dir, base_file_id, imgName + '_' + str(hand_id) + '.png')
            continue
          
      # end of all hands
      new_js_line = json.dumps(js) + "\n"
      new_json_file.write(new_js_line)
    new_json_file.close()
    print('write ' + base_file_id + '.json')
  print('add_hand_phone_status done.')
  print('ignore_hand:%d'%(ignore_hand_num))
  print('phone_normal:%d, phone_backhand:%d, phone_hard:%d'%(phone_normal_num, phone_backhand_num, phone_hard_num))
  print('nophone_bg:%d, nophone_face:%d, nophone_susp:%d'%(nophone_bg_num, nophone_face_num, nophone_susp_num))
    
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('Usage: add_hand_phone_status.py org_json_dir done_root_dir dst_json_dir')
    exit()
  org_json_dir = sys.argv[1]
  dst_json_dir = sys.argv[2]
  done_root_dir = sys.argv[3]
  add_hand_phone_status(org_json_dir, dst_json_dir, done_root_dir)
