#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/6/18 下午7:38
"""
import sensor_msgs.msg
import message_filters
from cv_bridge import CvBridge
import threading
import numpy as np
from typing import List

from .dto import Target, Transform, Euler, Point
import rospy
from copy import deepcopy


class TopicReader:
    def __init__(self, topic: str, class_type, queue_size=1, msg_process_func=lambda x: x):
        self.sub = rospy.Subscriber(topic, class_type, callback=self.__callback, queue_size=queue_size)
        self.con = threading.Condition()
        self.data = None
        self.func = msg_process_func

    def __callback(self, msg):
        with self.con:
            self.data = self.func(msg)
            self.con.notify()

    def read(self):
        with self.con:
            self.con.wait()
            return self.data

    def release(self):
        self.sub.unregister()

    @staticmethod
    def read_once(topic, class_type, msg_process_func=lambda x: deepcopy(x)):
        data = class_type()
        con = threading.Condition()

        def __callback(msg: class_type):
            nonlocal data, con, msg_process_func
            with con:
                data = msg_process_func(msg)
                con.notifyAll()

        sub = rospy.Subscriber(topic, class_type, callback=__callback)
        with con:
            con.wait()
            sub.unregister()
            return data


class ROSCameraKinectV2:
    def __init__(self):
        self.cam_info = TopicReader.read_once("/kinect2/hd/camera_info",
                                              sensor_msgs.msg.CameraInfo)
        self.cam_matrix = np.array(self.cam_info.P).reshape((3, 4))[:, :3]

        self.color_react_sub = message_filters.Subscriber("/kinect2/hd/image_color_rect", sensor_msgs.msg.Image)
        self.depth_react_sub = message_filters.Subscriber("/kinect2/hd/image_depth_rect", sensor_msgs.msg.Image)
        self.ts = message_filters.TimeSynchronizer([self.color_react_sub, self.depth_react_sub], 10)
        self.ts.registerCallback(self.__callback)

        self.bridge = CvBridge()

        self.color = None
        self.depth = None
        self.con = threading.Condition()

    def __callback(self, color: sensor_msgs.msg.Image, depth: sensor_msgs.msg.Image):
        with self.con:
            self.color = self.bridge.imgmsg_to_cv2(color)
            self.depth = self.bridge.imgmsg_to_cv2(depth)
            self.con.notify()

    def read(self) -> (np.ndarray, np.ndarray):
        with self.con:
            self.con.wait()
            return self.color, self.depth

    def convert_pixel_to_world(self, d, pixel_pt: Point):
        x, y = pixel_pt.x, pixel_pt.y
        # d = depth[int(y), int(x)]
        fx, fy = self.cam_matrix[0, 0], self.cam_matrix[1, 1]
        cx, cy = self.cam_matrix[0, 2], self.cam_matrix[1, 2]
        world_x = (x - cx) / fx * d
        world_y = (y - cy) / fy * d
        return [world_x, world_y, float(d)]

    def convert_multi_pixel_to_world(self, d, pixel_pts) -> List:
        res = []
        for pt in pixel_pts:
            res.append(self.convert_pixel_to_world(d, pt))
        return res

    def convert_target_to_world(self, d, pixel_pt: Point) -> Target:
        x, y, z = self.convert_pixel_to_world(d, pixel_pt)
        return Target(Transform.build_from_euler_point(Euler(), Point(x / 1000.0, y / 1000.0, z / 1000.0)), "kinect2_link")
        #
        # Tools.gen_msg_pose_stamped(frame_id="kinect2_link",
        #                                        position=[x / 1000.0, y / 1000.0, z / 1000.0],
        #                                        orientation=[0.0, 0.0, 0.0]))

        # target.pose.header.frame_id = "kinect2_link"
        # target.pose.pose.position.x = world_pt[0]
        # target.pose.pose.position.y = world_pt[1]
        # target.pose.pose.position.z = world_pt[2]
        # target.pose.pose.orientation = Tools.rxyzdeg2qua(0.0, 0.0, 0.0)
