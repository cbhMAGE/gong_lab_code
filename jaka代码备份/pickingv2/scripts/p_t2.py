#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/12/22 上午4:58
"""
import open3d as o3d
import rospy
import sensor_msgs.msg
from base.ColorMapping import convert_numpy_2_pointcloud2_color
import numpy as np

rospy.init_node("pt2", anonymous=True)

pc: o3d.geometry.PointCloud = o3d.io.read_point_cloud("./data/0714120307_out.ply")

pub = rospy.Publisher("/cloud_in", sensor_msgs.msg.PointCloud2, queue_size=3)

pts = np.asarray(pc.points, dtype=np.float32)
# print(pts)
print(pts.shape)
print(pts.dtype)

pts = pts / 1000.0

pts[:, -1] -= 0.6
pts[:, 1] -= 0.75
pts[:, 0] += 0.4

tomatoes = np.array([
    [0.0, -0.3, 0.7],
    [0.2, -0.21, 0.45],
    [0.1, -0.23, 0.63],
    # [0.67, -0.23, 0.58],
    # [0.62, -0.23, 0.63],
    # [0.65, -0.36, 0.6],
], dtype=np.float32)

tomato_pub = rospy.Publisher("/tomato", sensor_msgs.msg.PointCloud2, queue_size=3)

c = 1000
r = rospy.Rate(10)
while not rospy.is_shutdown():
    msg = convert_numpy_2_pointcloud2_color(pts.copy(), frame_id="platform", maxDistColor=2)
    pub.publish(msg)

    # msg2 = convert_numpy_2_pointcloud2_color(tomatoes, frame_id="platform")
    # tomato_pub.publish(msg2)

    r.sleep()
    # c -= 1
