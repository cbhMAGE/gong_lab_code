#! /usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo
import message_filters
import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
 
def callback(data1,data2):
    bridge = CvBridge()
    color_image = bridge.imgmsg_to_cv2(data1, 'bgr8')
    depth_image = bridge.imgmsg_to_cv2(data2, '16UC1')
    depth = np.array(depth_image)
    np.save('/home/msi/1008_catkin_ws/src/realsenseD455_bridge/scripts/depth.npz',depth)
    cv2.imwrite('/home/msi/1008_catkin_ws/src/realsenseD455_bridge/scripts/rgb.jpg',color_image)
    #cv2.imwrite('/home/msi/1008_catkin_ws/src/realsenseD455_bridge/scripts/depth.jpg',depth_image)
    cv2.imshow('color_image',color_image)
    cv2.waitKey(1000)
    c_x = 640
    c_y = 360
    real_z = depth_image[c_y, c_x] * 0.001  
    real_x = (c_x- ppx) / fx * real_z
    real_y = (c_y - ppy) / fy * real_z
    rospy.loginfo("potion:x=%f,y=%f,z=%f",real_x,real_y,real_z) #输出图像中心点在相机坐标系下的x,y,z
 
if __name__ == '__main__':
    global fx, fy, ppx, ppy #相机内参
    fx = 637.009521484375
    fy = 636.3241577148438
    ppx = 629.4425048828125
    ppy = 375.2152404785156
    rospy.loginfo("realsense bridge test")
    rospy.init_node('get_image', anonymous=True)
 
    color = message_filters.Subscriber("/camera/color/image_raw", Image)
    depth = message_filters.Subscriber("/camera/depth/image_rect_raw", Image)
    color_depth = message_filters.ApproximateTimeSynchronizer([color, depth], 10, 1, allow_headerless=True)
    color_depth.registerCallback(callback)  
    #同时订阅/camera/color/image_raw和/camera/aligned_depth_to_color/image_raw话题，并利用message_filters实现话题同步，共同调用callback
    rospy.spin()
