#####################################################
#  Copyright (C) 2017 Wan Sheng, NCTU, Taiwan 
#  ALL RIGHTS RESERVED
#####################################################
# import library
from random import shuffle
import sqlite3 as sq

# path setting
aflw_sq_path = '/HardDisk/WD/AFLW/aflw/data/aflw.sqlite'
# random shuffle or not
random_shuffle = True
# text file name
label_file_name = "aflw_label.txt"



# open the sqlite file which contains the informataion of AFLW dataset
aflw_sq = sq.connect(aflw_sq_path)
aflw_cur = aflw_sq.cursor()
print "Succesfully open the aflw.sqlite"


# show the tables in the database
aflw_cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
table_name = aflw_cur.fetchall()
for item in table_name:
    print item

# fetch image_name, face_rect and feature coordinates from db
faces = aflw_cur.execute("SELECT * FROM Faces")
face_ids = faces.fetchall();


face_names = []
face_rects = []
face_features = []
for i in range(len(face_ids)): 
    # get face_id and file_id
    face_id = face_ids[i][0]
    file_id_sqlite = "SELECT file_id FROM Faces WHERE face_id ='" + str(face_id) + "'"
    file_id = aflw_cur.execute(file_id_sqlite).fetchall()
    file_id = file_id[0][0]
    if len(file_id) < 1:
        continue
    
    # get file_path
    face_name_query = "SELECT filepath FROM FaceImages WHERE file_id = '"+ file_id + "'"
    face_name = aflw_cur.execute(face_name_query).fetchall()
    face_name = face_name[0][0]

    # rect
    feature_rect_query = "SELECT FaceRect.x,FaceRect.y,FaceRect.w,FaceRect.h FROM FaceRect WHERE face_id ='" + str(face_id) + "'"
    feature_rect = aflw_cur.execute(feature_rect_query).fetchall()
    if len(feature_rect) < 1:
        continue
    
    feature_rect = feature_rect[0]
    x = feature_rect[0]
    y = feature_rect[1]
    w = feature_rect[2]
    h = feature_rect[3]
    
    # coor (normalize to 0~1)
    feature_coor_query = "SELECT descr,FeatureCoords.x,FeatureCoords.y FROM FeatureCoords,FeatureCoordTypes WHERE face_id ='" + str(face_id) + "' AND FeatureCoords.feature_id = FeatureCoordTypes.feature_id"
    feature_coor = aflw_cur.execute(feature_coor_query).fetchall()    
    coor_x = [-1 for k in range(5)]
    coor_y = [-1 for k in range(5)]
    for j in range(len(feature_coor)):
        if feature_coor[j][0] == 'LeftEyeCenter':
            coor_x[0] = (feature_coor[j][1] - x)/w
            coor_y[0] = (feature_coor[j][2] - y)/h
        elif feature_coor[j][0] == 'RightEyeCenter':
            coor_x[1] = (feature_coor[j][1] - x)/w
            coor_y[1] = (feature_coor[j][2] - y)/h
        elif feature_coor[j][0] == 'NoseCenter':
            coor_x[2] = (feature_coor[j][1] - x)/w
            coor_y[2] = (feature_coor[j][2] - y)/h
        elif feature_coor[j][0] == 'MouthLeftCorner':
            coor_x[3] = (feature_coor[j][1] - x)/w
            coor_y[3] = (feature_coor[j][2] - y)/h
        elif feature_coor[j][0] == 'MouthRightCorner':
            coor_x[4] = (feature_coor[j][1] - x)/w
            coor_y[4] = (feature_coor[j][2] - y)/h
    
    coor = []
    coor.append(coor_x)
    coor.append(coor_y)
    
    # append to list
    face_names.append(face_name)
    face_rects.append(feature_rect)
    face_features.append(coor)

aflw_cur.close()
aflw_sq.close()

# check list size
if len(face_names) != len(face_rects) or len(face_names) != len(face_features):
    print "Inconsistent list size:"
    print len(face_names), len(face_rects), len(face_features)

# record the list to the text file
label_file = open(label_file_name,"w")
label_file.write("image_name LeftEyeCenter.x LeftEyeCenter.y" + \
                " RightEyeCenter.x RightEyeCenter.y" + \
                " NoseCenter.x NoseCenter.y" + \
                " MouthLeftCorner.x MouthLeftCorner.y" + \
                " MouthRightCorner.x MouthRightCorner.y\n")

index = range(len(face_names))
if random_shuffle == True:
    shuffle(index)
for i in index:
    label_file.write(face_names[i] + " " + str(face_features[i][0][0]) + " " + str(face_features[i][1][0]) \
                                + " " + str(face_features[i][0][1]) + " " + str(face_features[i][1][1]) \
                                + " " + str(face_features[i][0][2]) + " " + str(face_features[i][1][2]) \
                                + " " + str(face_features[i][0][3]) + " " + str(face_features[i][1][3]) \
                                + " " + str(face_features[i][0][4]) + " " + str(face_features[i][1][4]) + "\n")

label_file.close()