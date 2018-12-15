import os
import sys
import shutil
import numpy as np
import json
import cv2
import random
import glob
import dms_json
import dms_utils
import dataset_all

def image_random_rotate(img, cx, cy, thelta, scale):
  if len(img.shape) == 3:
    rows,cols,channels = img.shape
  else:
    rows,cols = img.shape
  rand_thelta = random.uniform(-1.0, 1.0)*thelta
  rand_scale = 1.0 #random.uniform(1.0/scale, scale)
  M = cv2.getRotationMatrix2D((cx,cy), rand_thelta, rand_scale)
  dst = cv2.warpAffine(img, M, (cols, rows), flags=cv2.INTER_LINEAR, \
                       borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
  return dst
  
# rect1, rect2: left, top, right, bottom
def calc_iou(rect1, rect2):
  overlap_x = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
  overlap_y = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
  area_ol = overlap_x*overlap_y
  area1, area2 = (rect1[2] - rect1[0])*(rect1[3] - rect1[1]), (rect2[2] - rect2[0])*(rect2[3] - rect2[1])
  if area_ol == 0 or area1 == 0 or area2 == 0:
    return 0
  return (area_ol*1.0/(area1 + area2 - area_ol))
  
def crop_samples(img, crop_box, save_sample_path, img_file_name):
  resize_width, resize_height = 150, 150
  x,y,w,h = int(crop_box[0]), int(crop_box[1]), int(crop_box[2] - crop_box[0]), int(crop_box[3] - crop_box[1])
  #if x < 0 or y < 0 or w <= 0 or h <= 0:
  #  #print 'Error: invalid position, ', x, y, w, h, img_file_name
  #  return None
  cx, cy = x + w/2, y + h/2
  img_width, img_height = np.size(img, 1), np.size(img, 0)
  
  w_p = w
  h_p = h
  x_p, y_p = int(cx - w_p/2), int(cy - h_p/2)
  
  pad_top = max(-y_p, 0)
  pad_left = max(-x_p, 0)
  pad_bottom = max(y_p + h_p - img_height, 0)
  pad_right = max(x_p + w_p - img_width, 0)
  frame_padding = cv2.copyMakeBorder(img, pad_top, pad_bottom, pad_left, pad_right, cv2.BORDER_CONSTANT, value=[0,0,0])
  dst_image = frame_padding[y_p+pad_top:y_p+pad_top+h_p, x_p+pad_left:x_p+pad_left+w_p]
  dst_image = cv2.resize(dst_image, (resize_width, resize_height), interpolation = cv2.INTER_LINEAR)
  dst_image_name = save_sample_path + '/' + img_file_name
  cv2.imwrite(dst_image_name, dst_image)
  return

def rand_crop_samples(img, crop_box, save_sample_path, img_file_name):
  # Empty
  return
  
def crop_train_test_samples(img, crop_box, save_sample_path, img_file_name, flag_train):
  if not os.path.exists(save_sample_path):
    os.makedirs(save_sample_path)
  if flag_train == 0:
    crop_samples(img, crop_box, save_sample_path, img_file_name) # for submodule test
  else:
    rand_crop_samples(img, crop_box, save_sample_path, img_file_name) # add rand crop
  return
  
def crop_to_small_images(json_dir, img_dir, save_dir, class_type, flag_train):
  """
    @json_dir - the folder includes annotated json files
    @img_dir - the folder includes images corresponding to 'json_dir'
    @save_dir - the path to save cropped and classified images
    @class_type - 'smoke' or 'phone'
    @flag_train - 0 or 1
  """
  if not (class_type == 'hand'):
    print ('Unsupported class type: ', class_type)
    return
  
  print('test2')
  print(json_dir)
  for json_file_name in glob.glob(json_dir + '/*.json'):
    print('test1')
    json_file = open(json_file_name, 'r')
    base_file_name = os.path.basename(json_file_name)
    print (base_file_name)

    # json file name to the 'save_dir'
    json_fn_pfx = os.path.splitext(base_file_name)[0] # e.g. 1132.json -> 1132
    save_subdir = os.path.join(save_dir, json_fn_pfx) # /.../1234/
    if os.path.exists(save_subdir):
      shutil.rmtree(save_subdir)
    
    lines = json_file.read().splitlines()
    img_count = 0
    for line in lines:
      if line[0] == '#':
        continue
      image_arrt = dms_json.DMSJsonParser() # create a DMSJsonParser object
      # Parse all labels
      if image_arrt.ParseJsonRaw(line) == False:
        print ('parse json attribute failed: ', image_arrt.imgName)
        continue
      #if image_arrt.hasDriver == False:
      #  print 'Driver not exist: ', image_arrt.imgName
      #  continue
      #if len(image_arrt.driverLandmark) == 0:
      #  print 'Landmark is empty: ', image_arrt.imgName
      #  continue
      if image_arrt.handNum <= 0:
        continue
      
      img_path = os.path.join(img_dir, json_fn_pfx, image_arrt.imgName)
      if os.path.isfile(img_path) == False:
        #print 'Image file is not exist, ', img_path
        continue
      img = cv2.imread(img_path, -1) # read as org image
      if img is None:
        print ('img is None, ', img_path)
        continue
      img_count = img_count + 1
      if img_count%200 == 0:
        print (img_count)
      
      for hand_idx in range(image_arrt.handNum):
        handId = image_arrt.handInfos[hand_idx].handId
        handBox = image_arrt.handInfos[hand_idx].handBox
        handPhoneStatus = image_arrt.handInfos[hand_idx].handPhoneStatus
        #if handPhoneStatus != 'unknown':
        #  continue # already checked
        crop_box = [0, 0, 0, 0]
        cx, cy = (handBox[0] + handBox[2])/2, (handBox[1] + handBox[3])/2
        w, h = handBox[2] - handBox[0], handBox[3] - handBox[1]
        w = max(w, h)
        h = w
        crop_box[0] = cx - w
        crop_box[1] = cy - h
        crop_box[2] = cx + w
        crop_box[3] = cy + h # so crop_box_w = 2*w and crop_box_h = 2*h
        
        # get samples
        save_sample_path = save_subdir + '/hand_' + image_arrt.imgType
        crop_train_test_samples(img, crop_box, save_sample_path, image_arrt.imgName + '_' + str(handId) + '.png', flag_train)
        
    print ('all ', img_count, ' images processed.')
  print ('all json files done.')

if __name__ == '__main__':
  if len(sys.argv) < 2:
    '''
	print 
      Usage: python crop_to_small_images.py data_type data_name save_dir class_type
       data_type -- 'train' or 'test'
       data_name -- data name, like 'patch_201805'
       save_dir -- the path to save cropped images, like workspace/xxxx/example_0916
       class_type -- 'smoke'
       flag_train -- 0 or 1, 0 -- only for check, 1 -- add rand crop
    '''
    exit()
    
  data_type = sys.argv[1]  # 'train', 'test'
  data_name = sys.argv[2]  # 'patch_201805'
  json_dir, img_dir = dataset_all.GetDatabase(data_name, data_type)
  save_dir = os.path.join(sys.argv[3], data_name)
  class_type = sys.argv[4]
  flag_train = int(sys.argv[5])
  print(json_dir,img_dir,save_dir)
  crop_to_small_images(json_dir, img_dir, save_dir, class_type, 0)
  