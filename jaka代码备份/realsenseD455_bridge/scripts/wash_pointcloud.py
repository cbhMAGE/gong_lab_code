#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# 订阅realsense-ros发布的点云，然后进行点云中间处理，最后进行发布

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
        self.sub = rospy.Subscriber("/kinect2/hd/points",
                                     PointCloud2,
                                     self.callback, queue_size=20)
    def callback(self, msg):
        assert isinstance(msg, PointCloud2)

        # gen=point_cloud2.read_points(msg,field_names=("x","y","z","rgb"))
        points = point_cloud2.read_points_list(
            msg, field_names=("x", "y", "z","rgb"),skip_nans=True)

        new_points = []

        for point in points:
            z = point[2]
            if z<1.0:
                new_points.append(point)

        _msg = PointCloud2()
        _msg.header.stamp = rospy.Time().now()
        _msg.header.frame_id = "kinect2_rgb_optical_frame"

        if len(new_points) == 3:
            _msg.height = new_points.shape[1]
            _msg.width = new_points.shape[0]
        else:
            _msg.height = 1
            _msg.width = len(new_points)
        print(float_to_bin(new_points[0][3]))
        _msg.fields = [
            PointField('x', 0, PointField.FLOAT32, 1),
            PointField('y', 4, PointField.FLOAT32, 1),
            PointField('z', 8, PointField.FLOAT32, 1),
            PointField('rgb', 12, PointField.UINT32, 1)]
        _msg.is_bigendian = False
        _msg.point_step = 16
        _msg.row_step = _msg.point_step * len(new_points)
        _msg.is_dense = True
        _msg.data = np.asarray(new_points, np.float32).tostring()

        pub.publish(_msg)

if __name__ =='__main__':
    pub = rospy.Publisher('/kinect2/hd/points_washed', PointCloud2, queue_size=5)
    rospy.init_node("pointcloud_washer")
    PointCloudSubscriber()
    rate = rospy.Rate(30)
    
    rospy.spin()