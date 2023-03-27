#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author: zhiyu YANG
@Email: ZhiyuYANG96@outlook.com
@Date: 2022-01-20 13:45:16
"""
import rospy
import numpy as np

import sensor_msgs.msg
from planner.base import State

rospy.init_node("plan_test", anonymous=True)

pub = rospy.Publisher("/custom_joint_states", sensor_msgs.msg.JointState, queue_size=1, latch=True)
msg = sensor_msgs.msg.JointState()
msg.name = ['joint_1', 'joint_2', 'joint_3']

start_state = State(np.deg2rad([30, -50, 30]))
goal_state = State(np.deg2rad([60, -20, -10]))

r = rospy.Rate(1)
f = True
while not rospy.is_shutdown():
    pub.publish(msg)
    if f:
        msg.position = start_state.to_list()
    else:
        msg.position = goal_state.to_list()
    f = not f
    r.sleep()
