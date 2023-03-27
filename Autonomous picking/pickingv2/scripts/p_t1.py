#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/12/21 下午12:48
"""
import numpy as np

import rospy
import sensor_msgs.msg
from base.ColorMapping import color_map
import rospy
from base.ColorMapping import convert_numpy_2_pointcloud2_color

if __name__ == '__main__':
    rospy.init_node("pcpc", anonymous=True)
    pts = np.array([
        [0.0, -0.5, 0.3],
        [0.0, -0.54, 0.4],
        [0.0, -0.55, 0.5],
        [0.0, -0.43, 0.6],
        [0.0, -0.5, 0.7],
        [0.0, -0.52, 0.7],
        [0.08, -0.53, 0.7],
        [0.05, -0.53, 0.7],

        [0.2, -0.4, 0.3],
        [0.1, -0.53, 0.7],
        [0.2, -0.5, 0.7],

        [0.25, -0.3, 0.7],
        [0.3, -0.3, 0.4],
        [0.3, -0.3, 0.7],
        [0.3, -0.27, 0.7],
        [0.3, -0.25, 0.7],
        [0.3, -0.20, 0.7],

        # [0.75, -0.2, 0.7],
        # [0.8, -0.2, 0.7],
        # [0.85, -0.2, 0.65],
        # [0.85, -0.27, 0.65],
        # [0.85, -0.27, 0.6],
        # [0.85, -0.27, 0.55],
        # [0.85, -0.27, 0.50],
        # [0.85, -0.27, 0.45],
    ], dtype=np.float32)

    # tomatoes = np.array([
    #     [0.4, -0.17, 0.6],
    #     [0.45, -0.21, 0.65],
    #     [0.5, -0.23, 0.63],
    # ], dtype=np.float32)

    # ai die
    # tomatoes = np.array([
    #     [0.05, -0.17, 0.6],
    #     [0.45, -0.21, 0.65],
    #     [0.62, -0.23, 0.63],
    #     [0.2, -0.21, 0.45],
    #     [0.1, -0.23, 0.63],
    #     [0.67, -0.23, 0.58],
    # ], dtype=np.float32)

    tomatoes = np.array([
        [0.0, -0.3, 0.7],
        [0.2, -0.21, 0.45],
        [0.1, -0.23, 0.63],
        # [0.67, -0.23, 0.58],
        # [0.62, -0.23, 0.63],
        # [0.65, -0.36, 0.6],
    ], dtype=np.float32)

    pub = rospy.Publisher("/cloud_in", sensor_msgs.msg.PointCloud2, queue_size=3)
    tomato_pub = rospy.Publisher("/tomato", sensor_msgs.msg.PointCloud2, queue_size=3)
    r = rospy.Rate(10)
    c = 3
    while not rospy.is_shutdown() and c > 0:
        msg = convert_numpy_2_pointcloud2_color(pts, frame_id="platform", maxDistColor=1.0)
        pub.publish(msg)
        msg2 = convert_numpy_2_pointcloud2_color(tomatoes, frame_id="platform")
        tomato_pub.publish(msg2)
        r.sleep()
        # c -= 1
    rospy.spin()
