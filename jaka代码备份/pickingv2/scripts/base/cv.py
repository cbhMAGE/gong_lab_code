#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/11/9 下午6:12
"""
import numpy as np

from .capture import ROSCameraKinectV2
from .dto import Target, Point
import rospy
from cv_bridge import CvBridge
import cv2
import pickingv2.msg
import pickingv2.srv
import geometry_msgs.msg
import sensor_msgs.msg
from typing import List


class CV:
    def __init__(self):
        self.srv = rospy.ServiceProxy("target_detection_srv", pickingv2.srv.TargetDetectionSrv)
        self.cv_bridge = CvBridge()
        self.cap = ROSCameraKinectV2()
        # cv2.namedWindow("cv", cv2.WINDOW_GUI_NORMAL)
        # cv2.resizeWindow("cv", 1600, 900)

        self.failure_img = np.ones((1080, 1920, 3), dtype=np.uint8)
        cv2.putText(self.failure_img, "Failure", (500, 500), cv2.FONT_HERSHEY_PLAIN, 10, (255, 120, 120), thickness=1)

    def depth_fill(self, x, y, depth_img):
        def get_left(_x, _y, _depth_img):
            left_pixel = _x
            while (left_pixel > 0) and (_depth_img[_y, left_pixel] == 0) and (left_pixel > _x - 10):
                left_pixel = left_pixel - 1
            return _depth_img[_y, left_pixel]

        def get_right(_x, _y, _depth_img):
            right_pixel = _x
            while (right_pixel < 1920) and (_depth_img[_y, right_pixel] == 0) and (right_pixel < _x + 10):
                right_pixel = right_pixel + 1
            return _depth_img[_y, right_pixel]

        def get_top(_x, _y, _depth_img):
            top_pixel = _y
            while (top_pixel > 0) and (_depth_img[top_pixel, _x] == 0) and (top_pixel > _y - 10):
                top_pixel = top_pixel - 1
            return _depth_img[top_pixel, _x]

        def get_bottom(_x, _y, _depth_img):
            bottom_pixel = _y
            while (bottom_pixel < 1080) and (_depth_img[bottom_pixel, _x] == 0) and (bottom_pixel < _y + 10):
                bottom_pixel = bottom_pixel + 1
            return _depth_img[bottom_pixel, _x]

        if not (0 <= y < 1080 and 0 <= x < 1920):
            return 0
        z = depth_img[y, x]
        available = 0
        res = 0
        if z == 0:
            left = get_left(x, y, depth_img)
            right = get_right(x, y, depth_img)
            top = get_top(x, y, depth_img)
            bottom = get_bottom(x, y, depth_img)
            for dep in [left, right, top, bottom]:
                if dep != 0:
                    res = res + dep
                    available = available + 1

            z = res / available if available != 0 else 0
            # print(left, right, top, bottom)
        else:
            z = depth_img[y, x]
        return z

    def get_cv_result(self, repeat_cap_read_num=0) -> (List[Target], np.ndarray):
        for _ in range(repeat_cap_read_num):
            self.cap.read()
        color, depth = self.cap.read()

        req = pickingv2.srv.TargetDetectionSrvRequest()
        req.img = self.cv_bridge.cv2_to_imgmsg(color)
        resp: pickingv2.srv.TargetDetectionSrvResponse = self.srv(req)
        if not resp.success:
            return [], self.failure_img.copy()

        # cv2.imshow("cv", self.cv_bridge.imgmsg_to_cv2(resp.result_img))
        # cv2.waitKey(1)
        targets = []
        if resp.poses2d:
            for index, pose in enumerate(resp.poses2d):
                pose: geometry_msgs.msg.Pose2D = pose
                _d = self.depth_fill(int(pose.x), int(pose.y), depth)
                if _d == 0:
                    continue
                t = self.cap.convert_target_to_world(_d, Point(pose.x, pose.y))
                t.set_name(f"{index:d}")
                targets.append(t)
        return targets, self.cv_bridge.imgmsg_to_cv2(resp.result_img)
