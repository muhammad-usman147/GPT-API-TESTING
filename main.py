
from flask import *  
from yolo_car_count import CarCount
import time
import threading
import json
import cv2 
import os 
app = Flask(__name__)  
###initializing necesarry params
labelsPath='yolo-coco/coco.names'
weights='yolo-coco/yolov3.weights'
cfgPath='yolo-coco/yolov3.cfg'
confidence = 0.5
threshold = 0.8

def stream_template(template_name, **context):
    app.update_template_context(context)
    t = app.jinja_env.get_template(template_name) 
    rv = t.stream(context)
    rv.disable_buffering()
    return rv

def fsaf(obj):
    count = 0
    OUTPUT = {}
    while True:
        (grabbed, frame) = obj.videoStream.read()
        if not grabbed:
            break 
        frame = cv2.resize(frame, (640,384))
        results = obj.GetCarCount(frame)
        OUTPUT[f"Frame{count}"] = results
        print(results)
        with open("results.json",'w') as f:
            json.dump(OUTPUT,f)
        count += 1
    print("Done..!!!")
            

class TimeFrame():
    def __init__(self) -> None:
        self.start_time = None
        self.end_time = None 
        self.frame_rate = []
        self.L1_avg = []
        self.L2_avg = []
        self.L3_avg = []
        self.under_the_bridge = []
        self.avg_vehicle_count = []
        self.jump=0
        self.previous = 0 

object = TimeFrame()

def GetFiles():
    ls = [i for i in os.listdir() if i.endswith('.MP4')]
    ls = {"files":ls}
    return ls
FPS = 0
@app.route('/')  
def main():  
    ls = GetFiles()
    return render_template("form.html", ls=ls)  
  
@app.route('/detector', methods=['POST','GET'])  
def detect(): 
    print(request.method )
    if request.method == 'POST':  
        f = request.form['dropdown']
        minute_fps = int(request.form['fps-min'])
        if f == '':
            return render_template("form.html")
 
        obj = CarCount(VideoInput=f , OutputPath = 'cutout.MP4',labelsPath=labelsPath,
                        weights=weights,cfgPath=cfgPath,confidence = confidence, threshold = threshold, 
                        UseGPU = False)
        global FPS
        FPS = obj.videoStream.get(cv2.CAP_PROP_FPS)
        
        FPS = 5
        #FPS = (FPS*60) * minute_fps

        obj.video_width=640
        obj.video_height=384
        # def result():
        #     while True:
        #         (grabbed, frame) = obj.videoStream.read()

        #         if not grabbed:
        #             break
        #         results = obj.GetCarCount(frame)

        #         print(results)
        #         yield render_template('dashboard.html',rows=results)
        #         time.sleep(2) 
        threading.Thread(target=fsaf,args=(obj,)).start()
        ls = GetFiles()
        object.start_time = 0
        object.end_time = FPS
        object.jump = FPS 
        return render_template("form.html",isTraining = True,ls=ls)  
    else:
        ls = GetFiles()
        return render_template("form.html",ls=ls)  

@app.route("/dashboard")
def dashboard():
    with open("results.json") as read:
        data = json.load(read)
    length = len(list(data.keys()))
    framex = [i+1 for i in range(length)]
    vechile_count = []
    uniqueVehicles = []
    AverageLane1Speed = {"Frames":[],"AvgSpeed":[]}
    AverageLane2Speed = {"Frames":[],"AvgSpeed":[]}
    AverageLane3Speed = {"Frames":[],"AvgSpeed":[]}
    BelowTheBridge = {"Frames":[],"AvgSpeed":[]}
    
    for f in framex[object.start_time:object.end_time]:
        temp = data[f"Frame{f-1}"]['Total Vehicles']
        vechile_count.append(temp - object.previous)
        object.previous = temp

        #getting total vechicles
        temp = data[f"Frame{f-1}"]['Total Vehicles']
        uniqueVehicles.append(temp)

        #getting Lane 1 Speed
        temp2 = 0
        if data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L1 Speed'] !=  []:
            
            speed = data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L1 Speed']
            print("--->",speed)
            for v in speed:
                temp2 += v
            AverageLane1Speed['AvgSpeed'].append(temp2 /len(speed))
            AverageLane1Speed['Frames'].append(f"Frame{f}")

        #getting Lane2 Speed
        temp2 = 0
        if data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L2 Speed'] != []:
            
            speed = data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L2 Speed']    
            for v in speed:
                temp2 += v
            AverageLane2Speed['AvgSpeed'].append(temp2 /len(speed))
            AverageLane2Speed['Frames'].append(f"Frame{f}")

        #getting Lane3 Speed
        temp2 = 0
        if data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L3 Speed'] != []:
            
            speed = data[f'Frame{f-1}']["R1 Info"]['Vehicle Lane']['L3 Speed']    
            for v in speed:
                temp2 += v
            AverageLane3Speed['AvgSpeed'].append(temp2 /len(speed))
            AverageLane3Speed['Frames'].append(f"Frame{f}")


    for f in framex:
        temp2 = 0
        if data[f'Frame{f-1}']["R2 Info"]['Vehicle Speed'] != []:
            
            speed = data[f'Frame{f-1}']["R2 Info"]['Vehicle Speed']   
            for v in speed:
                temp2 += v
            BelowTheBridge['AvgSpeed'].append(temp2 /len(speed))
            BelowTheBridge['Frames'].append(f"Frame{f}")


        #getting Average OutGoing Speed
    TotalUniqueCars = data[f"Frame{length-1}"]['Total Vehicles']

    
    if AverageLane1Speed['AvgSpeed'] != []:
        object.L1_avg.append(sum(AverageLane1Speed['AvgSpeed'])//len(AverageLane1Speed['Frames']))
    if AverageLane2Speed['AvgSpeed'] != []:
        object.L2_avg.append(sum(AverageLane2Speed['AvgSpeed'])//len(AverageLane2Speed['Frames']))
    if AverageLane3Speed['AvgSpeed'] != []:
        object.L3_avg.append(sum(AverageLane3Speed['AvgSpeed'])//len(AverageLane3Speed['Frames']))
    if BelowTheBridge['AvgSpeed'] != []:
        object.under_the_bridge.append(sum(BelowTheBridge['AvgSpeed'])//len(BelowTheBridge['Frames']))
    if uniqueVehicles != []:
        object.avg_vehicle_count.append(sum(uniqueVehicles)/len(uniqueVehicles))
    object.frame_rate.append(object.end_time)
    
    

    object.start_time = object.end_time
    object.end_time += FPS
    Lanes = data[f'Frame{length-1}']['Lanes Count']
    return render_template('dashboard.html', Lanes=Lanes,
                                             framex=object.frame_rate,
                                             TotalUniqueCars = object.avg_vehicle_count,
                                             uniqueVehicles=uniqueVehicles,
                                             l1= object.L1_avg,
                                             l2=object.L2_avg,
                                             l3 = object.L3_avg,
                                             UTB = object.under_the_bridge)
if __name__ == '__main__':  
    app.run(debug=True)