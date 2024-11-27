##########
# This software is licensed under the GNU General Public License v3.0
# Copyright (c) 2019-2020 Vassilis Bitsikas
##########
'''
Modify settings file before running
'''

import cv2
import numpy as np
import time
import datetime
import os
import PySpin
import imageio
from settings import *

########## INPUTS ###########
rig_pos = 11
record = False #Boolean to enable or disable video recording
resize = True #Boolean to resize frames before processing
#############################

def tracking(Exp_ID, rig_pos, t_pos, filechunk,record=False, resize = False):
    #camera selection and control
    print ("Recording: {}".format(record))
    date = datetime.datetime.now().strftime("%Y%m%d")

    # Retrieve singleton reference to system object
    system = PySpin.System.GetInstance()
    # Retrieve list of cameras from the system
    cam_list = system.GetCameras()
    # Retrieve the specific camera
    cam = cam_list.GetBySerial(str(cam_ID[rig_pos]))
    print('Device serial number retrieved: %s' % cam_ID[rig_pos])
    # Initialize camera
    cam.Init()
    cam.BeginAcquisition()
    # Retrieve GenICam nodemap
    nodemap = cam.GetNodeMap()

    # Get the current frame rate; acquisition frame rate recorded in hertz
    #
    # *** NOTES ***
    # The video frame rate can be set to anything; to
    # have videos play in real-time, the acquisition frame rate can be
    # retrieved from the camera.

    node_acquisition_framerate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
    framerate_to_set = node_acquisition_framerate.GetValue()
    print('Frame rate to be set to %d' % framerate_to_set)

    # Fetch frame
    image_result = cam.GetNextImage()
    width = image_result.GetWidth()
    height = image_result.GetHeight()


    # create trackbar for setting threshold
    def nothing(x):
        pass

    #create window
    cv2.namedWindow("{}_{} - Live thresholded".format(rig_pos,cam_ID[rig_pos]))

    #create threshold trackbar
    cv2.createTrackbar('threshold', "{}_{} - Live thresholded".format(rig_pos,cam_ID[rig_pos]), t_pos, 255, nothing)


    #Total hours to record
    end_time = datetime.datetime.now() + datetime.timedelta(hours=tot_hours)

    i = 0
    data = []
    time_counter = 0
    t0 = time.perf_counter()
    movie_number = 0


    #Start the loop
    while datetime.datetime.now() < end_time:
        image = cam.GetNextImage().GetData().reshape((height, width))[0:height_trim,0:width_trim]

        if resize:
            image = cv2.resize(image, None, fx=0.75, fy=0.75, interpolation=cv2.INTER_NEAREST)

        if record:
            if time_counter == 0:
                date_f = datetime.datetime.now().strftime("%Y%m%d")
                moviename = r"C:\Users\bitsik0000\SleepData\{}\{}\{}_{}\{}_{}.mp4".format(Exp_ID,date,rig_pos, cam_ID[rig_pos], date_f, movie_number)
                os.makedirs(os.path.dirname(moviename), exist_ok=True)
                writer = imageio.get_writer(moviename, fps=fps)

        t1 = time.perf_counter()
        dt = t1 - t0
        t0 = t1

        current_time = datetime.datetime.now().strftime("%y%m%d%H%M%S%f")
        t_pos = cv2.getTrackbarPos('threshold', "{}_{} - Live thresholded".format(rig_pos,cam_ID[rig_pos]))

        image_thresholded = cv2.threshold(image, t_pos, 255, cv2.THRESH_TOZERO_INV)[1]



        (contours, _) = cv2.findContours(image_thresholded.copy(), cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)


        if len(contours) > 0:
            contourOI_ = max(contours, key=cv2.contourArea)
            area = cv2.contourArea(contourOI_)
            if area > 0:
                contourOI = cv2.convexHull(contourOI_)
                M = cv2.moments(contourOI)
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])



        cv2.putText(image_thresholded, "dt: {:.4f}, time: {}".format(dt, datetime.datetime.now().strftime("%y.%m.%d %H:%M:%S.%f")),
                    (30, 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=255)
        cv2.putText(image_thresholded, "Framenum: {}".format(i), (30, image_thresholded.shape[0] - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=255)
        data.append((i, dt, int(current_time), cX, cY, area))
        if record:
            cv2.putText(image,"dt: {:.4f}, time: {}".format(dt, datetime.datetime.now().strftime("%y.%m.%d %H:%M:%S.%f")),
                        (30, 30), cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=255)
            cv2.putText(image, "Framenum: {}".format(i), (30, image.shape[0] - 30),
                        cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, color=255)
            writer.append_data(image)


        #################

        cv2.drawContours(image_thresholded, contourOI, -1, 255, 2)
        cv2.circle(image_thresholded, (cX, cY), 4, 255, -1)
        cv2.imshow("{}_{} - Live thresholded".format(rig_pos,cam_ID[rig_pos]), image_thresholded)
        cv2.imshow("{}_{} - Live".format(rig_pos,cam_ID[rig_pos]), image)


        if cv2.waitKey(1) == 27:
           break

        i+=1
        time_counter += dt
        if time_counter >= filechunk:
            datanp = np.array(data)
            date_f = datetime.datetime.now().strftime("%Y%m%d")
            filename = r"C:\Users\bitsik0000\SleepData\{}\{}\{}_{}\{}_{}.csv".format(Exp_ID,date,rig_pos, cam_ID[rig_pos], date_f, movie_number)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            np.savetxt(filename, datanp, delimiter= ",")
            data = []
            time_counter = 0
            movie_number += 1
            if record:
                writer.close()



    cam.close_cam()



tracking(Exp_ID[rig_pos],rig_pos,t_pos,filechunk,record=record, resize= resize)
