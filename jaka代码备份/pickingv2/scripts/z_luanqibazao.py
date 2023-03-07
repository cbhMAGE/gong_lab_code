#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/25 下午6:53
"""
import threading
import rospy
import pickingv2.msg
import pickingv2.srv
import qjaka_gui.srv
import moveit_msgs.msg
import cv2
import numpy as np
import cv_bridge
import geometry_msgs.msg
import trajectory_msgs.msg
from base.dto import RobotConfig
import moveit_commander
from base.tools import moveit_error_code_to_string
from typing import List
from copy import deepcopy

mg = moveit_commander.MoveGroupCommander("left_arm")
mg.set_start_state_to_current_state()
mg.set_joint_value_target(
    [-1.5707963267948966, 1.5707963267948966, -0.8726646259971648, 3.490658503988659, 2.96705972839036, .5])
success, plan, planning_time, error_code = mg.plan()
print(mg.get_current_state())
print("+" * 20)
print(plan)
print("+" * 20)
p = mg.retime_trajectory(
    mg.get_current_state(), plan, velocity_scaling_factor=0.8,
    acceleration_scaling_factor=0.8,
    algorithm='time_optimal_trajectory_generation'
)
print(p)

# dual = moveit_commander.MoveGroupCommander("dual_arm")
# print("+++++++++++++++++++++")
# print(dual.get_current_state())
# rospy.init_node("dd")
# r = rospy.Rate(1)
# while not rospy.is_shutdown():
#     print(time.time())
#     r.sleep()
