########## Modify before each experiment ##########
#Declarative assignment
Exp_ID = {
  **dict.fromkeys([1,2,3,4,5,6,7,8], 241127),
  **dict.fromkeys([9,10,11,12,13,14,15,16], )
}

# #Universal assignment
# Exp_ID = 200428
###################################################
# Modify only if necessary
t_pos = 36 #43 #Initial threshold value for image processing
filechunk = 60*60 #Duration (in seconds) that data is 'chunked' into for saving
width_trim = 1280 #initial trimming of video before tracking processing
height_trim = 960 #initial trimming of video before tracking processing
tot_hours = 24000
fps = 30
# get the camera ID from rig position
cam_ID = {1: 19105133,
          2: 19105135,
          3: 19105131,
          4: 19105134,
          5: 19105130,
          6: 19139245,
          7: 19139237,
          8: 19105129,
          9: 19139251,
          10: 19139246,
          11: 19105115,
          12: 16466083,
          13: 19105132,
          14: 19139244,
          15: 19105128,
          16: 19139234
          }
