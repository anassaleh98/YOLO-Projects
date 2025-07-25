# Import Libraries and Load Model
import cv2
import pandas as pd
import numpy as np
from ultralytics import YOLO
from tracker import *

# Load YOLOv8 Model
model=YOLO('yolov8s.pt')

cap = cv2.VideoCapture('peoplecount1.mp4')


# Define Entry/Exit Zones
area1 = [(312,388),(289,390),(474,469),(497,462)]  # exit
area2 = [(279,392),(250,397),(423,477),(454,469)]  # entry

def RGB(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE :  
        print([x, y])
        
cv2.namedWindow('RGB')
cv2.setMouseCallback('RGB', RGB)

cap=cv2.VideoCapture('peoplecount1.mp4') # Open Video File


#  Load COCO Class Names
my_file = open("coco.txt", "r")
data = my_file.read()
class_list = data.split("\n")
#print(class_list)


people_entering = {}
people_exiting = {}
entering = set()
exiting = set()
tracker = Tracker()


while True:    
    ret,frame = cap.read()    # Reads frame by frame and resizes the frame
    if not ret:
        break
    frame=cv2.resize(frame,(1020,500))

    results=model.predict(frame)
    # print('results',results[0])
    a=results[0].boxes.data 
    #print("a",a) 
    px = pd.DataFrame(a.cpu().numpy()).astype("float")
    # print(px)
    list=[]
             
    for index,row in px.iterrows():
        #print(row)        # [ 30,  50, 100, 200, 0.91, 0],  # person
 
        x1=int(row[0])
        y1=int(row[1])
        x2=int(row[2])
        y2=int(row[3])
        d=int(row[5])
        c=class_list[d]
        
        if 'person' in c:
           list.append([x1,y1,x2,y2])  
           
    bbox_id = tracker.update(list)
    
    for bbox in bbox_id:
        x3,y3,x4,y4,id = bbox
        # people entering
        results = cv2.pointPolygonTest(np.array(area2,np.int32) ,((x4,y4)) , False )
        if results >=0:
            people_entering[id] = (x4,y4)
            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
            
        if id in people_entering:
            results1 = cv2.pointPolygonTest(np.array(area1,np.int32) ,((x4,y4)) , False )
            if results1 >=0:
                cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
                cv2.circle(frame , (x4,y4) , 10 , (255,0,255),-1)
                cv2.putText(frame,str(c),(x3,y3-10),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,255,255),1)
                cv2.putText(frame,str(id),(x3+65,y3-10),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,0,255),1)
                entering.add(id)
        
        # people exiting
        results2 = cv2.pointPolygonTest(np.array(area1,np.int32) ,((x4,y4)) , False )
        if results2 >=0:
            people_exiting[id] = (x4,y4)
            cv2.rectangle(frame,(x3,y3),(x4,y4),(0,255,0),2)
        if id in people_exiting:
            results3 = cv2.pointPolygonTest(np.array(area2,np.int32) ,((x4,y4)) , False )
            if results3 >=0:
                cv2.rectangle(frame,(x3,y3),(x4,y4),(0,0,255),2)
                cv2.circle(frame , (x4,y4) , 10 , (255,0,255),-1)
                cv2.putText(frame,str(c),(x3,y3-10),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,255,255),1)
                cv2.putText(frame,str(id),(x3+55,y3-10),cv2.FONT_HERSHEY_COMPLEX,(0.5),(255,0,255),1)
                exiting.add(id)
            
               
    cv2.polylines(frame,[np.array(area1,np.int32)],True,(255,0,0),2)
    cv2.putText(frame,str('1'),(504,471),cv2.FONT_HERSHEY_COMPLEX,(1),(0,0,0),2)

    cv2.polylines(frame,[np.array(area2,np.int32)],True,(255,0,0),2)
    cv2.putText(frame,str('2'),(466,485),cv2.FONT_HERSHEY_COMPLEX,(1),(0,0,0),2)
    
    i = len(entering)
    o = len(exiting)
    cv2.putText(frame,'Number of entering people= '+str(i),(20,44),cv2.FONT_HERSHEY_COMPLEX,(1),(0,255,0),2)
    cv2.putText(frame,'Number of exiting people= '+str(o),(20,82),cv2.FONT_HERSHEY_COMPLEX,(1),(0,0,255),2)
    

    cv2.imshow("RGB", frame)
    
    if cv2.waitKey(1)&0xFF==27:
        break

cap.release()
cv2.destroyAllWindows()








