#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/6/13 下午5:24
"""
import threading
import rospy
from detect_0613 import TargetDetection
import pickingv2.srv
import geometry_msgs.msg
from cv_bridge import CvBridge


class MainApplication:
    def __init__(self):
        self.detector = TargetDetection()
        self.cv_bridge = CvBridge()
        self.srv = rospy.Service("target_detection_srv", pickingv2.srv.TargetDetectionSrv, self._callback)
        self.lock = threading.Lock()

    def _callback(self, req: pickingv2.srv.TargetDetectionSrvRequest):
        resp = pickingv2.srv.TargetDetectionSrvResponse()
        resp.success = False
        resp.desc = "exception occurred"
        try:
            res, result_img = self.detector.image_detection(self.cv_bridge.imgmsg_to_cv2(req.img))
            resp.success = True
            resp.desc = ""
            for x, y, alpha in res.position:
                p = geometry_msgs.msg.Pose2D()
                p.x = x
                p.y = y
                resp.poses2d.append(p)
            resp.result_img = self.cv_bridge.cv2_to_imgmsg(result_img)
        except Exception as e:
            rospy.logerr("exec_cv failed")
            print(e)
        finally:
            return resp


if __name__ == '__main__':
    rospy.init_node("cv_node")
    app = MainApplication()
    rospy.spin()
