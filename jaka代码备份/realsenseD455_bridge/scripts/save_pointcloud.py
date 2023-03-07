#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# 订阅realsense-ros发布的点云，然后进行点云中间处理，最后进行发布
import ctypes
from unittest import skip
import numpy as np
import rospy
from sensor_msgs.msg import PointCloud2
from sensor_msgs import point_cloud2
from sensor_msgs.msg import PointField
import struct

def float_to_bin(num):
    return format(struct.unpack('!I', struct.pack('!f', num))[0], '032b')

class PointCloudSubscriber(object):
    def __init__(self) -> None:
        self.sub = rospy.Subscriber("pointcloud_topic",
                                     PointCloud2,
                                     self.callback, queue_size=20)
    # def callback(self, msg):
    #     assert isinstance(msg, PointCloud2)

    #     # gen=point_cloud2.read_points(msg,field_names=("x","y","z","rgb"))
    #     points = point_cloud2.read_points_list(
    #         msg, field_names=("x", "y", "z","rgb"))

    #     new_points = []

    #     for point in points:
    #         z = point[2]
    
    def callback(self, msg):
        print("callback")

        xyz = np.array([[0,0,0]])
        rgb = np.array([[0,0,0]])
        #self.lock.acquire()
        points = point_cloud2.read_points_list(
            msg, field_names=("x", "y", "z","rgb"))
        
        file = open('/home/msi/1008_catkin_ws/src/realsenseD455_bridge/saved_points_for_charpter_4_section_2_1/cloud1.xyz','w')
        #向文件中输入字符串
        

        for point in points:
            x = point[0]
            y = point[1]
            z = point[2]
            r = (point[3] & 0x00FF0000)>> 16
            g = (point[3] & 0x0000FF00)>> 8
            b = (point[3] & 0x000000FF)
            file.write(str(x)+" "+str(y)+" "+str(z)+" "+str(r)+" "+str(g)+" "+str(b)+"\n")
        file.close()
        print("saved")

if __name__ =='__main__':
    rospy.init_node("pointcloud_saver")
    PointCloudSubscriber()
    rospy.spin()