#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@author:yzy
@file:workspace.py
@time:2022/01/17
"""
from typing import Tuple
from base import State, SE, Space
import numpy as np
import rospy
from ik import AnalyticalIK
import moveit_msgs.srv
import moveit_msgs.msg
from dto import Transform, RobotConfig, Quaternion, Point


class PlanarWorkspace:
    def __init__(self, upper_bound, lower_bound, slices: Tuple):
        self.space = Space(lower_bound, upper_bound)
        self.dim = 2
        self.slices = slices
        self.free_vols = np.ones(slices, dtype=np.float64)

    def project_to_region(self, s: State) -> Tuple:
        pt = self.fk(s).to_point()
        coord = []
        for idx, val in enumerate(pt):
            coord.append(int(val // self.slices[idx]))
        return tuple(coord)

    @staticmethod
    def fk(s: State) -> Transform:
        pass

    @staticmethod
    def ik(s: Transform) -> State:
        pass

    def get_freevol(self, rid: Tuple) -> float:
        return self.free_vols[rid]

    @staticmethod
    def sample_rotation():
        return np.random.random() * 2 * np.pi

    def sample_from_region(self, rid) -> State:
        s = self.space.cut(rid, self.slices).sample_uniform(num=1)[0]
        return self.ik(SE(s, self.sample_rotation()))


class SE3Workspace(PlanarWorkspace):

    def __init__(self, upper_bound, lower_bound, slices: Tuple):
        super().__init__(upper_bound, lower_bound, slices)
        self.aik = AnalyticalIK(prefix="right_", robot_type='zu7_v2')
        self.fk = rospy.ServiceProxy(
            "/compute_fk", moveit_msgs.srv.GetPositionFK)
        self.state_valid_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)
        self.state_valid_srv.wait_for_service()
        self.state_valid_req = moveit_msgs.srv.GetStateValidityRequest()
        self.state_valid_req.robot_state.joint_state.name = [f"right_joint_{i:d}" for i in range(1, 7)]
        self.state_valid_req.group_name = 'right_arm'
        self.free_vols[(1, 3, 2)] = 0.8
        self.free_vols[(2, 2, 2)] = 0.9
        # todo: free_vols from ros

    def fk(self, s: State) -> Transform:
        prefix = "right_"
        req = moveit_msgs.srv.GetPositionFKRequest()
        req.robot_state = (RobotConfig.build_from_jvals(
            s.data.tolist(), prefix)).to_robot_states()
        req.fk_link_names = [f"{prefix}link_6"]
        resp: moveit_msgs.srv.GetPositionFKResponse = self.fk(req)
        return Transform.build_from_pose_msg(resp.pose_stamped[0])

    def ik(self, s: SE) -> State:
        tf = Transform.build_from_qua_point(
            Quaternion(*s.rotation), Point(*s.point))
        sols = self.aik.solve(tf)
        np.random.shuffle(sols)
        return State(sols[0])

    @staticmethod
    def sample_rotation():
        u1, u2, u3 = np.random.uniform([0, 0, 0], [1, np.pi * 2, np.pi * 2])
        a = np.sqrt(1 - u1)
        b = np.sqrt(u1)
        return a * np.sin(u2), a * np.cos(u2), b * np.sin(u3), b * np.cos(u3)

    def check_state(self, s:State)->bool:
        self.state_valid_req.robot_state.joint_state.position = s.data
        resp: moveit_msgs.srv.GetStateValidityResponse = self.state_valid_srv(self.state_valid_req)
        return resp.valid