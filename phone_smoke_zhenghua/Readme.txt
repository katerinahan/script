
每次做自标注之前，先从本地机上拷贝dataset_all.py文件进行更新


I.抽烟的自标注步骤：
1.首先利用smoke_check文件夹下面的脚本，check_smoke_small_image.py 
每个数据集可以放在一个check*.sh里面，比如
python check_smoke_small_images.py train neimeng_ruilian_front_20181127 ./check_small_images/smoke_check_1201 smoke 1
这样能在目标文件夹得到所需要分类的抽烟小样本
2.对抽烟的小样本更新之后，利用脚本add_common_box_smoke_region.py
把smoke region的标注自动加上去，比如
python add_common_box_smoke_region.py org_json_dir dst_json_dir done_root_dir



II.打电话的自标注步骤：
1.首先利用phone_check文件夹下面的脚本，check_hand_small_images.py
python check_hand_small_images.py train lightside njsmoke ./check_small_images/phone_check_1201 hand 1
这样能在目标文件夹得到所需要分类的手的小样本
2.对hand的小样本更新之后，利用脚本add_hand_phone_status.py
把phone status的标注自动加上去，比如
python add_hand_phone_status.py org_json_dir dst_json_dir done_root_dir