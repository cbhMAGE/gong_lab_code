#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/2/26 下午7:03
"""

import time
import logging

import numpy as np
from typing import Dict, List, Tuple, Union, Iterable

import std_msgs.msg

from planner.tools import Timer

import rospy
import moveit_msgs.msg
import moveit_msgs.srv
import trajectory_msgs.msg
import geometry_msgs.msg
import visualization_msgs.msg
import tf.transformations

from planner.base import Space, State, Magic, wrap_to_pi
from planner.prm import PRM
# from planner.stp import STP, Decomposition
from planner.stp2 import STP2, Decomposition
from scripts.planner.stp import Cell
from copy import deepcopy

logging.basicConfig(level=logging.INFO)


class PlanarSpace(Space):
    def __init__(self, lower_bound, upper_bound):
        super().__init__(lower_bound, upper_bound, check_motion_resolution=np.deg2rad(10))

        self.check_validity_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)
        self.planned_path_pub = rospy.Publisher("/move_group/display_planned_path", moveit_msgs.msg.DisplayTrajectory,
                                                queue_size=1, latch=True)

    def check_validity(self, s: State) -> bool:
        req = moveit_msgs.srv.GetStateValidityRequest()
        req.group_name = 'arm'
        req.robot_state.joint_state.name = ['joint_1', 'joint_2', 'joint_3']
        req.robot_state.joint_state.position = s.to_list()
        resp: moveit_msgs.srv.GetStateValidityResponse = self.check_validity_srv.call(req)
        return resp.valid

    def pub_path(self, states: List[State]):
        pts = []
        epoch_time = 3  # s
        start_time = 0
        add_num = 8
        for idx in range(1, len(states)):
            for t, positions in zip(np.linspace(start_time, start_time + epoch_time, add_num),
                                    np.linspace(states[idx - 1].data_view, states[idx].data_view, add_num)):
                pts.append(trajectory_msgs.msg.JointTrajectoryPoint(
                    positions=positions.tolist(),
                    time_from_start=rospy.Duration.from_sec(t)
                ))
            start_time += epoch_time

        msg = moveit_msgs.msg.DisplayTrajectory()
        msg.trajectory_start.joint_state.name = ['joint_1', 'joint_2', 'joint_3']
        msg.trajectory_start.joint_state.position = states[0].to_list()
        msg.trajectory = [moveit_msgs.msg.RobotTrajectory(
            joint_trajectory=trajectory_msgs.msg.JointTrajectory(
                joint_names=['joint_1', 'joint_2', 'joint_3'],
                points=pts
            ))]
        self.planned_path_pub.publish(msg)


class PlanarDecomposition(Decomposition):

    def __init__(self, workspace_: Space, slices_: Tuple):
        super().__init__(workspace_, slices_)
        self.ik_srv = rospy.ServiceProxy("/compute_ik", moveit_msgs.srv.GetPositionIK)
        self.fk_srv = rospy.ServiceProxy("/compute_fk", moveit_msgs.srv.GetPositionFK)
        self.decomposition_pub = rospy.Publisher("/visualization_decomposition", visualization_msgs.msg.MarkerArray, queue_size=1,
                                                 latch=True)

        self.cells[(10, 9)].w = 2.0

    @staticmethod
    def _afk(s: State) -> State:
        return State([
            0.5 * np.cos(s[0], dtype=Magic.DATA_TYPE) + 0.4 * np.cos(s[0] + s[1], dtype=Magic.DATA_TYPE) + 0.1 * np.cos(
                s[0] + s[1] + s[2], dtype=Magic.DATA_TYPE),
            0.5 * np.sin(s[0], dtype=Magic.DATA_TYPE) + 0.4 * np.sin(s[0] + s[1], dtype=Magic.DATA_TYPE) + 0.1 * np.sin(
                s[0] + s[1] + s[2], dtype=Magic.DATA_TYPE),
            s[0] + s[1] + s[2]
        ])

    def _moveit_fk(self, s: State) -> State:
        req = moveit_msgs.srv.GetPositionFKRequest()
        req.robot_state.joint_state.name = ['joint_1', 'joint_2', 'joint_3']
        req.robot_state.joint_state.position = s.to_list()
        req.fk_link_names = ["link_ee"]
        req.header.frame_id = "base_link"
        resp: moveit_msgs.srv.GetPositionFKResponse = self.fk_srv.call(req)
        pose_stamped: geometry_msgs.msg.PoseStamped = resp.pose_stamped[0]
        qua = pose_stamped.pose.orientation
        angles = tf.transformations.euler_from_quaternion([
            qua.x, qua.y, qua.z, qua.w
        ])
        return State([pose_stamped.pose.position.x, pose_stamped.pose.position.y, angles[-1]])

    def fk(self, s: State) -> State:
        return self._moveit_fk(s)

    @staticmethod
    def _aik(workspace_s: State) -> List[State]:
        a, b, c = 0.5, 0.4, 0.1
        x, y, theta = workspace_s.data_view
        xx = x - c * np.cos(theta, dtype=Magic.DATA_TYPE)
        yy = y - c * np.sin(theta)
        d = np.sqrt(xx * xx + yy * yy)
        if d > (a + b) or d < abs(a - b):
            return []
        q = np.arctan2(yy, xx)
        if d == (a + b):
            return [State(wrap_to_pi([q, 0, theta - q]))]
        if d == abs(a - b):
            return [State(wrap_to_pi([q, np.pi, theta - q - np.pi]))]

        tmp = (a * a + d * d - b * b) / (2 * a * d)
        q1 = -np.arccos(tmp) + q
        q12 = np.arccos(tmp) + q
        tmp = (a * a + b * b - d * d) / (2 * a * b)
        q2 = np.pi - np.arccos(tmp)
        return [State(wrap_to_pi([q1, q2, theta - q1 - q2])),
                State(wrap_to_pi([q12, -q2, theta - q12 + q2]))]

    def _moveit_ik(self, workspace_s: State) -> List[State]:
        req = moveit_msgs.srv.GetPositionIKRequest()
        req.ik_request.group_name = 'arm'
        req.ik_request.robot_state.joint_state.name = ['joint_1', 'joint_2', 'joint_3']
        req.ik_request.robot_state.joint_state.position = [0.54327257, -0.5, 0]
        req.ik_request.ik_link_name = "link_ee"
        req.ik_request.pose_stamped.header.frame_id = "base_link"
        req.ik_request.timeout = rospy.Duration.from_sec(1.0)
        req.ik_request.pose_stamped.pose.position.x = workspace_s[0]
        req.ik_request.pose_stamped.pose.position.y = workspace_s[1]
        req.ik_request.pose_stamped.pose.position.z = 0.0
        qua = tf.transformations.quaternion_from_euler(0, 0, workspace_s[2], 'sxyz')
        req.ik_request.pose_stamped.pose.orientation.x = qua[0]
        req.ik_request.pose_stamped.pose.orientation.y = qua[1]
        req.ik_request.pose_stamped.pose.orientation.z = qua[2]
        req.ik_request.pose_stamped.pose.orientation.w = qua[3]
        resp: moveit_msgs.srv.GetPositionIKResponse = self.ik_srv.call(req)
        if resp.error_code.val == resp.error_code.SUCCESS:
            return [State(resp.solution.joint_state.position)]

    def _sample_in_cell(self, cell: Cell, seed=None) -> Union[State, None]:
        pt, = cell.space.sample_uniform(num=1)
        angle = np.random.uniform(-np.pi, np.pi)
        if seed is not None and np.random.random() < 0.75:
            angle = self.fk(seed).data_view[-1]
        states = self._aik(State([*pt.data_view, angle]))
        if not states:
            return None
        if seed is None:
            return states[np.random.randint(0, len(states))]
        else:
            return min(states, key=lambda _s: np.linalg.norm(_s.data_view[:2] - seed.data_view[:2]))

    def publish(self):
        self.publish_cells(list(rid for rid in self.cells), (0, 0.8, 0.8, 0.5), msg_id=1)

    def publish_cells(self, cells: Iterable[Cell], rgba: Tuple, msg_id=2):
        msg_array = visualization_msgs.msg.MarkerArray()
        msg = visualization_msgs.msg.Marker()
        msg.header.frame_id = "base_link"
        msg.ns = "decomposition"
        msg.id = msg_id
        msg.type = msg.CUBE_LIST
        msg.action = msg.ADD
        msg.scale.x = self.interval[0]
        msg.scale.y = self.interval[1]
        msg.scale.z = 0.1
        msg.pose.position.z = -0.5
        msg.pose.orientation.w = 1.0
        color = std_msgs.msg.ColorRGBA(*rgba)
        msg.color = color
        msg.lifetime = rospy.Duration.from_sec(0.0)

        for cell in cells:
            c = (cell.space.lower_bound + cell.space.upper_bound) / 2.0
            if len(c) == 2:
                c = (*c, 0)
            msg.points.append(geometry_msgs.msg.Point(*c))
        msg_array.markers.append(msg)

        msg = visualization_msgs.msg.Marker()
        msg.header.frame_id = "base_link"
        msg.ns = "decomposition"
        msg.lifetime = rospy.Duration.from_sec(0.0)
        msg.scale.z = self.interval[0] / 4
        msg.pose.position.z = -0.5
        msg.pose.orientation.w = 1.0
        msg.action = msg.ADD
        msg.color = std_msgs.msg.ColorRGBA(0.5, 1.0, 1.0, 1.0)
        for idx, cell in enumerate(cells):
            msg.id = msg_id + idx + 1
            msg.type = msg.TEXT_VIEW_FACING
            msg.text = str(cell.rid)
            c = (cell.space.lower_bound + cell.space.upper_bound) / 2.0
            msg.pose.position.x = c[0]
            msg.pose.position.y = c[1]
            msg_array.markers.append(deepcopy(msg))
        self.decomposition_pub.publish(msg_array)


rospy.init_node("planar_demo_node")

space = PlanarSpace(
    np.deg2rad([-180, -180, -180]),
    np.deg2rad([180, 180, 180]),
)

start_state = State(np.deg2rad([30, -50, 30]))
goal_state = State(np.deg2rad([60, -20, -10]))

# +++ test prm ++++++++++++++++++++++++++++++++++++++++++++
# prm = PRM(space_=space)
# sols = prm.solve(start_state, goal_state)
# print(sols)
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++

decomposition = PlanarDecomposition(
    Space([-1.1, -1.1], [1.1, 1.1]),
    (13, 13)
)

# coord = decomposition.fk(State([0.1, 0.5, 0.3]))
# print(coord)
# print(decomposition.ik(State([*coord.data_view, 0.9])))
# print(decomposition.aik(State([*coord.data_view, 0.9])))

stp = STP2(space_=space, decomposition_=decomposition)
sols = stp.solve(start_state, goal_state)
print("solved")
print(sols)

rate = rospy.Rate(1)
while not rospy.is_shutdown():
    # space.pub_path(sols)
    # decomposition.publish()
    rate.sleep()
    # break
