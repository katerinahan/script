import os, sys
import glob
import json
import codecs

def get_smoke_phone_infos(dataset_json_dir, save_info_name):
  save_file = codecs.open(save_info_name, "w", "utf-8")
  save_file.close()
  save_file = codecs.open(save_info_name, "a+", 'utf-8')
  write_line = 'id image_num smoke_nohand smoke_hand smoke_hard nosmoke_bg nosmoke_face nosmoke_susp nosmoke_cover'
  write_line += ' nohand ignore_hand phone_normal phone_backhand phone_hard nophone_face nophone_susp nophone_bg'
  write_line +=' head_count ' \
                 'head_ignore_no_count  ' \
                 'head_ignore_yes_count ' \
                 'hand_count hand_ignore_no_count hand_ignore_yes_count\n'
  save_file.write(write_line)
  
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

    head_count, head_ignore_no_count, head_ignore_yes_count = 0, 0, 0
    hand_count, hand_ignore_no_count, hand_ignore_yes_count = 0, 0, 0
    
    json_lines = json_file.read().splitlines()
    for line in json_lines:
      if line[0] == '#':
        image_num += 1
        continue
      js = json.loads(line)
      imgName = js["image_key"]
      image_num += 1
      
      # smoke
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
      
      # phone
      if not 'hand' in js:
        nohand_num += 1
      else:
        for idx in range(len(js['hand'])):
          if 'ignore' in js['hand'][idx]['attrs']:
            if js['hand'][idx]['attrs']['ignore'] == 'yes':
              ignore_hand_num += 1
              continue
          
          if 'phone_status' in js['hand'][idx]['attrs']:
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
			  
			  
 # head & hand
      if 'head' in js.keys():
        head_count += len(js['head'])
        for idx in range(len(js['head'])):
          if 'ignore' in js['head'][idx]['attrs']:
            if js['head'][idx]['attrs']['ignore'] == 'no':
              head_ignore_no_count += 1
            else:
              head_ignore_yes_count += 1

      if 'hand' in js.keys():
        hand_count += len(js['hand'])
        for idx in range(len(js['hand'])):
          if 'ignore' in js['hand'][idx]['attrs']:
            if js['hand'][idx]['attrs']['ignore'] == 'no':
              hand_ignore_no_count += 1
            else:
              hand_ignore_no_count += 1
    # end of all lines
    
    write_line = base_file_id + ' %d'%(image_num)
    write_line += ' %d %d %d %d %d %d %d'%(smoke_nohand_num, smoke_hand_num, smoke_hard_num, nosmoke_bg_num, nosmoke_face_num, nosmoke_susp_num, nosmoke_cover_num)
    write_line += ' %d %d %d %d %d %d %d %d '%(nohand_num, ignore_hand_num, phone_normal_num, phone_backhand_num, phone_hard_num, nophone_face_num, nophone_susp_num, nophone_bg_num)
    write_line += ' %d %d %d %d %d %d\n' % (head_count, head_ignore_no_count, head_ignore_yes_count, hand_count, hand_ignore_no_count, hand_ignore_yes_count)
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
