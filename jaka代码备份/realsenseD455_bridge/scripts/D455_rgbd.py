#! /usr/bin/env python
import rospy
from std_msgs.msg import String
from sensor_msgs.msg import Image, CameraInfo
import message_filters
import cv2
from cv_bridge import CvBridge, CvBridgeError


def callback(data1,data2):
    bridge = CvBridge()
    color_image = bridge.imgmsg_to_cv2(data1, 'bgr8')
    depth_image = bridge.imgmsg_to_cv2(data2, '16UC1')
    # print(len(depth_image[0]))
    # print(len(color_image[0]))
    for i in range(720):
        for j in range(1280):
            real_z = depth_image[i][j] * 0.001  
            real_x = (j- ppx) / fx * real_z
            real_y = (i - ppy) / fy * real_z
            if(real_z > 1 or real_x>1 or real_y>1):
                # print(real_z)
                color_image[i][j] = [0,0,0]
    cv2.imshow('color_image',color_image)
    cv2.imwrite("color_image.jpg",color_image)
    cv2.imwrite("depth_image.jpg",depth_image)
    cv2.waitKey(1)

 
if __name__ == '__main__':
    global fx, fy, ppx, ppy #相机内参
    ppx,ppy,fx,fy = 629.4425048828125, 375.2152404785156, 637.009521484375, 636.3241577148438
    rospy.init_node('get_image', anonymous=True)
 
    color = message_filters.Subscriber("/camera/color/image_raw", Image)
    depth = message_filters.Subscriber("/camera/aligned_depth_to_color/image_raw", Image)
    color_depth = message_filters.ApproximateTimeSynchronizer([color, depth], 10, 1, allow_headerless=True)
    color_depth.registerCallback(callback)  
    #同时订阅/camera/color/image_raw和/camera/aligned_depth_to_color/image_raw话题，并利用message_filters实现话题同步，共同调用callback
    rospy.spin()