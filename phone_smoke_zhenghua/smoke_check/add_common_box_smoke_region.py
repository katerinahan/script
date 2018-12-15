import os
import sys
import glob
import shutil
import json
import codecs
from collections import OrderedDict

def getRegionClass(image_path, data_id, imgName):
  region_class = ['nosmoke_background', 'nosmoke_face', 'nosmoke_suspect', 'nosmoke_cover', 'smoke_hand', 'smoke_nohand', 'smoke_hard']
  label_class = ['nosmoke_bg', 'nosmoke_face', 'nosmoke_susp', 'nosmoke_cover', 'smoke_hand', 'smoke_nohand', 'smoke_hard']
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

def add_common_box_smoke_region(org_json_dir, dst_json_dir, done_root_dir):
  if not os.path.exists(dst_json_dir):
    os.makedirs(dst_json_dir)
  
  smoke_hand_num, smoke_nohand_num, smoke_hard_num = 0, 0, 0
  nosmoke_bg_num, nosmoke_face_num, nosmoke_susp_num, nosmoke_cover_num = 0, 0, 0, 0
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
      select_class = getRegionClass(done_root_dir, base_file_id, imgName)
      if select_class == None:
        new_json_file.write(line + '\n') #
        #print('Not Found: ', done_root_dir, base_file_id, imgName)
        continue
      #print select_class
      new_common_box = {}
      new_attrs = {}
      new_attrs['ignore'] = 'no'
      new_attrs['type'] = 'smoke_region'
      new_attrs['class'] = select_class
      new_common_box['attrs'] = new_attrs
      if select_class == 'smoke_hard':
        new_attrs['ignore'] = 'yes'
      
      # statistic
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
        print('Invalid smoke class.', select_class)
      
      # common box, like phone, hand
      if 'common_box' in js:
        js['common_box'].append(new_common_box)
      else:
        js['common_box'] = [new_common_box]
      new_js_line = json.dumps(js) + "\n"
      new_json_file.write(new_js_line)
    new_json_file.close()
    print('write ' + base_file_id + '.json')
  print('add_common_box_smoke_region done.')
  print('smoke_hand:%d, smoke_nohand:%d, smoke_hard:%d'%(smoke_hand_num, smoke_nohand_num, smoke_hard_num))
  print('nosmoke_bg:%d, nosmoke_face:%d, nosmoke_susp:%d, nosmoke_cover:%d'%(nosmoke_bg_num, nosmoke_face_num, nosmoke_susp_num, nosmoke_cover_num))
    
if __name__ == '__main__':
  if len(sys.argv) < 2:
    print('useage: add_common_box_smoke_region.py org_json_dir dst_json_dir done_root_dir')
    exit()
  org_json_dir = sys.argv[1]
  dst_json_dir = sys.argv[2]
  done_root_dir = sys.argv[3]
  add_common_box_smoke_region(org_json_dir, dst_json_dir, done_root_dir)
