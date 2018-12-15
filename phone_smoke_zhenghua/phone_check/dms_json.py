import json


# rect1, rect2: left, top, right, bottom
def calc_iou(rect1, rect2):
  overlap_x = max(0, min(rect1[2], rect2[2]) - max(rect1[0], rect2[0]))
  overlap_y = max(0, min(rect1[3], rect2[3]) - max(rect1[1], rect2[1]))
  area_ol = overlap_x*overlap_y
  area1, area2 = (rect1[2] - rect1[0])*(rect1[3] - rect1[1]), (rect2[2] - rect2[0])*(rect2[3] - rect2[1])
  if area_ol == 0 or area1 == 0 or area2 == 0:
    return 0
  return (area_ol*1.0/(area1 + area2 - area_ol))

def GetTightFaceBox(ldmks):
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  return face_box
  
class HandInfo(object):
  def __init__(self):
    self.handId = None
    self.handBox = None
    self.handPhoneStatus = 'unknown'
    self.handLeftRight = 'unknown'
    
class DMSJsonParser(object):
  def __init__(self):
    self.Reset()

  def _check(self, js):
    if 'face_keypoint_29' in js:
      self.key_keypoint = 'face_keypoint_29'
      return True
    elif 'face_keypoint_72' in js:
      self.key_keypoint = 'face_keypoint_72'
      return True
    elif 'face_keypoint_21' in js:
      self.key_keypoint = 'face_keypoint_21'
      return True
    elif 'face_keypoint_26' in js:
      self.key_keypoint = 'face_keypoint_26'
      return True
    elif 'face_keypoint_28' in js:
      self.key_keypoint = 'face_keypoint_28'
      return True
    elif 'face_keypoint_39' in js:
      self.key_keypoint = 'face_keypoint_39'
      return True
    else:
      return False

  def ParseJsonRaw(self, js_raw):
    js = json.loads(js_raw)
    self.imgName = js['image_key']

    if 'image_type' in js:
      self.imgType = js['image_type']
    
    # Face
    if 'head' in js:
      heads = js["head"]
      for head in heads:
        # Ignore those people who are not driver
        if head['attrs']['ignore'] == 'yes':
          continue
          
        # Face keypoint exist
        if self._check(js) == False:
          print(('face_keypoint not found:' + self.imgName))
          continue
        self.driverLandmark = js[self.key_keypoint][0]['data']
        tight_face_box = GetTightFaceBox(self.driverLandmark)
        
        if len(head['data']) != 4: # maybe many drivers, [null, null, null] to avoid CRASH
          #print('Found many drivers 1: ', self.imgName)
          continue
        if head['data'][0] == None: # maybe many drivers, [null, null, null] to avoid CRASH
          #print('Found many drivers 2: ', self.imgName)
          continue
        cur_iou = calc_iou(head['data'], tight_face_box)
        if cur_iou <= 0.001: # maybe many drivers, select the correct one, to avoid CRASH
          #print('Found many drivers 3: ', self.imgName)
          continue

        self.hasDriver = True   # IMPORTANT
        self.driverFaceBox = head['data']
        assert (len(self.driverFaceBox) == 4), '%d, %s'%(len(self.driverFaceBox), self.imgName)

        if 'smoke' in head['attrs']:
          if head['attrs']['smoke'] == 'yes':
            self.isSmoking = 1
          elif head['attrs']['smoke'] == 'unknown':
            self.isSmoking = -1

        # Pose value
        if 'yaw_value' in head['attrs'] and head['attrs']['yaw_value'] != 'unkonwn' and head['attrs']['yaw_value'] != 'unknown': # TODO: change to unknown
          self.hasPoseValue = True
          self.pose_yaw_value = float(head['attrs']['yaw_value'])
        if 'pitch_value' in head['attrs'] and head['attrs']['pitch_value'] != 'unkonwn' and head['attrs']['pitch_value'] != 'unknown':
          self.pose_pitch_value = float(head['attrs']['pitch_value'])
        if 'roll_value' in head['attrs'] and head['attrs']['roll_value'] != 'unkonwn' and head['attrs']['roll_value'] != 'unknown':
          self.pose_roll_value = float(head['attrs']['roll_value'])

    # Hand box
    if 'hand' in js:
      for hand_box in js["hand"]:
        hand_info = HandInfo()
        if 'ignore' in hand_box['attrs']:
          if hand_box['attrs']['ignore'] == 'no':
            hand_info.handId = hand_box['id']
            hand_info.handBox = hand_box['data']
            if 'phone_status' in hand_box['attrs']:
              hand_info.handPhoneStatus = hand_box['attrs']['phone_status']
            else:
              hand_info.handPhoneStatus = 'unknown'
            if 'left_or_right' in hand_box['attrs']:
              hand_info.handLeftRight = hand_box['attrs']['left_or_right']
            else:
              hand_info.handLeftRight = 'unknown'
              
            self.handNum += 1
            self.handInfos.append(hand_info)
        else:
          hand_info.handId = hand_box['id']
          hand_info.handBox = hand_box['data']
          if 'phone_status' in hand_box['attrs']:
            hand_info.handPhoneStatus = hand_box['attrs']['phone_status']
          else:
            hand_info.handPhoneStatus = 'unknown'
          if 'left_or_right' in hand_box['attrs']:
            hand_info.handLeftRight = hand_box['attrs']['left_or_right']
          else:
            hand_info.handLeftRight = 'unknown'
            
          self.handNum += 1
          self.handInfos.append(hand_info)
    elif 'common_box' in js:
      for common_box in js['common_box']:
        if (common_box['attrs']['type'] == 'hand' or 
           common_box['attrs']['type'] == 'left' or common_box['attrs']['type'] == 'right'):
          
          hand_info = HandInfo()
          if 'ignore' in common_box['attrs']:
            if common_box['attrs']['ignore'] == 'no':
              hand_info.handId = common_box['id']
              hand_info.handBox = common_box['data']
              if 'phone_status' in common_box['attrs']:
                hand_info.handPhoneStatus = common_box['attrs']['phone_status']
              else:
                hand_info.handPhoneStatus = 'unknown'
              if common_box['attrs']['type'] == 'left':
                hand_info.handLeftRight = 'left'
              elif common_box['attrs']['type'] == 'right':
                hand_info.handLeftRight = 'right'
              else:
                hand_info.handLeftRight = 'unknown'
                
              self.handNum += 1
              self.handInfos.append(hand_info)
          else:
            hand_info.handId = common_box['id']
            hand_info.handBox = common_box['data']
            if 'phone_status' in common_box['attrs']:
              hand_info.handPhoneStatus = common_box['attrs']['phone_status']
            else:
              hand_info.handPhoneStatus = 'unknown'
            if common_box['attrs']['type'] == 'left':
              hand_info.handLeftRight = 'left'
            elif common_box['attrs']['type'] == 'right':
              hand_info.handLeftRight = 'right'
            else:
              hand_info.handLeftRight = 'unknown'
              
            self.handNum += 1
            self.handInfos.append(hand_info)

    # common box, like phone, smoke
    if 'common_box' in js:
      common_boxes = js['common_box']
      for common_box in common_boxes:
        # Phone box
        if common_box['attrs']['type'] == 'phone':
          self.isCalling = 1
          self.phoneBox = common_box['data']
          if 'ignore' in common_box['attrs']:
            if common_box['attrs']['ignore'] == 'yes':
              self.isCalling = -1

        # Smoke region
        if common_box['attrs']['type'] == 'smoke_region':
          if 'ignore' in common_box['attrs']:
            if common_box['attrs']['ignore'] == 'no':
              self.smoke_region_class = common_box['attrs']['class']
          else:
            self.smoke_region_class = common_box['attrs']['class']
            
    return True

  def Reset(self):
    self.imgName = None
    self.imgType = 'unknown'
    self.hasDriver = False
    self.isSmoking = 0 # 0 -- not smoking, 1 -- smoking, -1 ---- ignore or unknown
    self.isCalling = 0 # 0 -- not calling, 1 -- calling, -1 --- ignore, phone invisible
    self.phoneBox = []
    self.driverFaceBox = []
    self.driverLandmark = ''
    self.key_keypoint = ''
    self.handNum = 0 # 0 -- no hand(or ignore), 1 -- one hand, 2 ---- two hands
    self.handInfos = []
    self.smoke_region_class = 'unknown'
    