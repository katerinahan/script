import os
import math
import numpy as np

def CropROIPadding(img, box, scale=1.0):
  """
    @face_box, [x1, y1, x2, y2]
  """
  x1, y1, x2, y2 = box[0], box[1], box[2], box[3]
  ih, iw = img.shape[:2]

  ## Get width and height of new box
  cx = (x1 + x2) / 2.
  cy = (y1 + y2) / 2.
  bw, bh = x2 - x1, y2 - y1
  bw, bh = bw*scale, bh*scale

  ## Get new coordinates
  x1 = int(max(cx - bw / 2., 0))
  x2 = int(min(cx + bw / 2., iw))
  y1 = int(max(cy - bh / 2., 0))
  y2 = int(min(cy + bh / 2., ih))
  crop_img = img[y1:y2, x1:x2]

  dtop = int(min((cy - bw / 2.), 0))
  dlft = int(min((cx - bw / 2.), 0))
  drht = int(min((iw - (cx + bh / 2.)), 0))
  dbtm = int(min((ih - (cy + bh / 2.)), 0))

  if (dtop < 0) or (dlft < 0) or (drht < 0) or (dbtm < 0):
    pad_img = cv2.copyMakeBorder(
        crop_img, abs(dtop), abs(dbtm), abs(dlft), abs(drht), cv2.BORDER_CONSTANT, value=[0, 0, 0])
  else:
    pad_img = crop_img

  return pad_img, [x1, y1, x2, y2]
  
def ConvertToLdmk21(ldmks_pts):
  """
  Parameters:
    @ldmks_pts:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  """
  if len(ldmks_pts) == 21:
    ldmks21 = ldmks_pts
  elif len(ldmks_pts) == 29:
    ldmk_29to21 = [0, 1, 2, 3, 4, 5, 6, 10, 8, 11, 15, 13, 17, 16, 18, 19, 20, 23, 24, 22, 21]
    ldmks21 = map(lambda i: ldmks_pts[i], ldmk_29to21)
  elif len(ldmks_pts) == 28:
    ldmk_28to21 = [0, 1, 2, 3, 4, 5, 6, 10, 8, 11, 15, 13, 17, 16, 18, 19, 20, 23, 24, 22, 21]
    ldmks21 = map(lambda i: ldmks_pts[i], ldmk_28to21)
  elif len(ldmks_pts) == 72:
    ldmk_72to21 = [22, 26, 39, 43, 13, 21, 17, 30, 38, 34, 50, 57, 53, 58, 60, 67, 70, 64, 62]
    ldmks21 = map(lambda i: ldmks_pts[i], ldmk_72to21)
  else:
    print('Error:', __name__, len(ldmks_pts), ldmks_pts)
    return []
  return ldmks21
  
def GetEyeBox(landmark_list):
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  
  # left
  pt_left, pt_right = ldmks[6], ldmks[8]
  left = pt_left[0]
  right = pt_right[0]
  width = pt_right[0] - pt_left[0]
  height = width
  cy = (pt_left[1] + pt_right[1])/2
  top = cy - height/2
  bottom = top + height
  left_eye_box = [left, top, right, bottom]
  
  # right
  pt_left, pt_right = ldmks[9], ldmks[11]
  left = pt_left[0]
  right = pt_right[0]
  width = pt_right[0] - pt_left[0]
  height = width
  cy = (pt_left[1] + pt_right[1])/2
  top = cy - height/2
  bottom = top + height
  right_eye_box = [left, top, right, bottom]
  
  return left_eye_box, right_eye_box
  
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
  
def GetMouthBox(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  Returns:
    - box, [x1, y1, x2, y2]
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  
  mouth_box = []
  for j in range(len(ldmks)):
    if j < 15: # starting from nose
      continue
    if len(mouth_box) == 0:
      mouth_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      mouth_box[0] = min(mouth_box[0], ldmks[j][0])
      mouth_box[1] = min(mouth_box[1], ldmks[j][1])
      mouth_box[2] = max(mouth_box[2], ldmks[j][0])
      mouth_box[3] = max(mouth_box[3], ldmks[j][1])
  
  return mouth_box
  
def GetPoseROI(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  face_box_width = face_box[2] - face_box[0]
  face_box_height = face_box[3] - face_box[1]
  
  cx = (face_box[0] + face_box[2])/2
  cy = (face_box[1] + face_box[3])/2
  
  scale_ratio = 2.0
  roi_width = max(face_box_width, face_box_height)*scale_ratio
  roi_height = roi_width
  
  roi = [0, 0, 0, 0]
  roi[0] = int(cx - roi_width/2)
  roi[1] = int(cy - roi_height/2)
  roi[2] = int(roi[0] + roi_width)
  roi[3] = int(roi[1] + roi_height)
  return roi
  
def GetSmokeROI(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  Returns:
    - box, [x1, y1, x2, y2]
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  face_box_width = face_box[2] - face_box[0]
  face_box_height = face_box[3] - face_box[1]
  
  cx = ldmks[nose_idx][0]
  cy = ldmks[nose_idx][1]
  scale_ratio = 1.4
  half_len = max(face_box_width, face_box_height)*scale_ratio / 2.
  
  roi = [0, 0, 0, 0]
  roi[0] = int(cx - half_len)
  roi[1] = int(cy - half_len)
  roi[2] = int(cx + half_len)
  roi[3] = int(cy + half_len)
  return roi
  
def GetSmokeROIBelow(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  face_box_width = face_box[2] - face_box[0]
  face_box_height = face_box[3] - face_box[1]
  
  scale_ratio = 1.3
  roi_width = max(face_box_width, face_box_height)*scale_ratio
  roi_height = roi_width
  
  mouth_box = GetMouthBox(ldmks)
  mouth_center = [(mouth_box[0] + mouth_box[2])/2.0, (mouth_box[1] + mouth_box[3])/2.0]
  #mouth_center = [(ldmks[17][0] + ldmks[18][0])/2., (ldmks[17][1] + ldmks[18][1])/2.]
  nose_bottom = max(max(ldmks[12][1], ldmks[13][1]), ldmks[14][1])
  
  roi_left = mouth_center[0] - roi_width/2
  roi_top = mouth_center[1] - roi_height/2 #max(mouth_center[1] - roi_height/2, nose_bottom)
  roi = [0, 0, 0, 0]
  roi[0] = int(roi_left)
  roi[1] = int(roi_top)
  roi[2] = int(roi_left + roi_width)
  roi[3] = int(roi_top + roi_height)
  return roi
  
def GetPhoneROI(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  face_box_width = face_box[2] - face_box[0]
  face_box_height = face_box[3] - face_box[1]
  
  dl = abs(ldmks[nose_idx][0] - face_box[0])
  cx = face_box[2] - dl
  du = abs(ldmks[nose_idx][1] - face_box[1])
  cy = face_box[3] - du
  
  scale_ratio = 2.0
  half_len = max(face_box_width, face_box_height)*scale_ratio / 2.
  
  roi = [0, 0, 0, 0]
  roi[0] = int(cx - half_len)
  roi[1] = int(cy - half_len)
  roi[2] = int(cx + half_len)
  roi[3] = int(cy + half_len)
  return roi
  
def GetPhoneROISide(landmark_list):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
  Returns:
    - box, [x1, y1, x2, y2]
  """
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21

  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None, None
  
  face_box = []
  for j in range(len(ldmks)):
    if len(face_box) == 0:
      face_box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      face_box[0] = min(face_box[0], ldmks[j][0])
      face_box[1] = min(face_box[1], ldmks[j][1])
      face_box[2] = max(face_box[2], ldmks[j][0])
      face_box[3] = max(face_box[3], ldmks[j][1])
  face_box_width = face_box[2] - face_box[0]
  face_box_height = face_box[3] - face_box[1]
  
  left_eye_box, right_eye_box = GetEyeBox(ldmks)
  left_eye_width = left_eye_box[2] - left_eye_box[0]
  right_eye_width = right_eye_box[2] - right_eye_box[0]
  
  le_pt = [(ldmks[6][0] + ldmks[8][0])/2 + left_eye_width/2, (ldmks[6][1] + ldmks[8][1])/2] # left_eye_corner_pt
  re_pt = [(ldmks[9][0] + ldmks[11][0])/2 - right_eye_width/2, (ldmks[9][1] + ldmks[11][1])/2] # right_eye_corner_pt
  
  left_eyebrow_up = min(min(ldmks[0][1], ldmks[1][1]), ldmks[2][1])
  right_eyebrow_up = min(min(ldmks[3][1], ldmks[4][1]), ldmks[5][1])
  
  scale_ratio = 2.0
  roi_height = max(face_box_height, face_box_width)*scale_ratio
  roi_width = roi_height
  
  left_cx = le_pt[0] - roi_height/3   # roi_height*2/3/2, for implying ear position
  right_cx = re_pt[0] + roi_height/3
  
  # left roi and right roi
  left_roi = [0, 0, 0, 0]
  left_roi[0] = int(left_cx - roi_width/2)
  left_roi[1] = left_eyebrow_up
  left_roi[2] = int(left_roi[0] + roi_width)
  left_roi[3] = int(left_roi[1] + roi_height)
  
  right_roi = [0, 0, 0, 0]
  right_roi[0] = int(right_cx - roi_width/2)
  right_roi[1] = right_eyebrow_up
  right_roi[2] = int(right_roi[0] + roi_width)
  right_roi[3] = int(right_roi[1] + roi_height)
  
  return left_roi, right_roi

def GetFaceBoxWithNoseCenter(landmark_list, center_method=0):
  """
  Parameters:
    @landmark_list:
      - ldmk_21, nose_idx = 13
      - ldmk_29, nose_idx = 16
      - ldmk_72, nose_idx = 57
    @center_method:
      - 0, use nose point as center and use mean value for reference
      - 1, use landmarks box center as returned box center
      - 2, use nose point as center and use maximum width and height for reference
  Returns:
    - None, Error
    - box, [x1, y1, x2, y2]
  """
  box = []
  ldmks_pts = [[float(i[0]), float(i[1])] for i in landmark_list]
  nose_idx = 13 # always use ldmk_21
  
  # Convert different ldmks to ldmk_21
  ldmks = ConvertToLdmk21(ldmks_pts)
  if len(ldmks) == 0:
    print('Error: Landmark is invalid.', __name__, len(ldmks_pts))
    return None
  for j in range(len(ldmks)):
    if len(box) == 0:
      box = [ldmks[j][0], ldmks[j][1], ldmks[j][0], ldmks[j][1]]
    else:
      box[0] = min(box[0], ldmks[j][0])
      box[1] = min(box[1], ldmks[j][1])
      box[2] = max(box[2], ldmks[j][0])
      box[3] = max(box[3], ldmks[j][1])
      
  if center_method == 0:
    cx = ldmks[nose_idx][0]
    cy = ldmks[nose_idx][1]
    half_len = (box[3] - box[1] + box[2] - box[0]) / 4.0
  elif center_method == 1: # typically for smoking
    cx = ldmks[nose_idx][0]
    cy = ldmks[nose_idx][1]
    half_len = max(box[3] - box[1], box[2] - box[0]) / 2.0
  elif center_method == 2: # typically for phone
    cx = (box[0] + box[2]) / 2.0
    cy = (box[1] + box[3]) / 2.0
    half_len = (box[3] - box[1] + box[2] - box[0]) / 4.0

    # Expand BOX according to the ratio between nose point and the two corners of the eye
    d0 = abs(box[2] - box[0]) # distance beween two corners of the eye
    dl = abs(ldmks[nose_idx][0] - box[0])
    dr = abs(ldmks[nose_idx][0] - box[2])
    half_len *= max(dl, dr) * 2 / d0
  elif center_method == 3: # typically for phone2
    dl = abs(ldmks[nose_idx][0] - box[0])
    cx = box[2] - dl
    du = abs(ldmks[nose_idx][1] - box[1])
    cy = box[3] - du
    half_len = max(box[3] - box[1], box[2] - box[0]) / 2.
  else:
    print('Error: center method is not supported.', __name__, center_method)
    return None
    
  box[0] = int(cx - half_len)
  box[1] = int(cy - half_len)
  box[2] = int(cx + half_len)
  box[3] = int(cy + half_len)
  return box
  
