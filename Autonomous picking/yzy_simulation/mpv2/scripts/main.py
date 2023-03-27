#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/4/18 下午12:36
"""
import time
from typing import Union, Tuple, List, Dict

import moveit_commander
import numpy as np
import rospy

from planner.stp import STP, Space, Decomposition, State, Magic, wrap_to_pi, Cell

import moveit_msgs.srv
import geometry_msgs.msg
import tf.transformations


class PlanarSpace(Space):
    def __init__(self, lb: Tuple, ub: Tuple):
        super().__init__(lb, ub)
        self.check_validity_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)

    def check_validity(self, s: State) -> bool:
        req = moveit_msgs.srv.GetStateValidityRequest()
        req.group_name = 'arm'
        req.robot_state.joint_state.name = ['joint_1', 'joint_2', 'joint_3']
        req.robot_state.joint_state.position = s.data_view.tolist()
        resp: moveit_msgs.srv.GetStateValidityResponse = self.check_validity_srv.call(req)
        return resp.valid


class PlanarDecomp(Decomposition):
    @staticmethod
    def _set_cell_free_vol(cells_dict: Dict[Tuple, Cell]):
        cells_dict[(7, 4)].free_vol = 0.1
        cells_dict[(6, 5)].free_vol = 0.1
        cells_dict[(3, 6)].free_vol = 0.1
        cells_dict[(2, 5)].free_vol = 0.1

    def _sample_in_cell(self, cell: Cell, seed: None or State) -> Union[State, None]:
        pt = cell.ws.sample_uniform().data_view
        if seed is not None and np.random.random() < 0.9:
            pt[-1] = self.fk(seed).data_view[-1]
        states = self._aik(State(*pt))
        if not states:
            return None
        if seed is None:
            return states[np.random.randint(0, len(states))]
        else:
            return min(states, key=lambda _s: np.linalg.norm(_s.data_view[:2] - seed.data_view[:2]))

    @staticmethod
    def _aik(ws_s: State) -> List[State]:
        a, b, c = 0.5, 0.4, 0.1
        x, y, theta = ws_s.data_view
        xx = x - c * np.cos(theta, dtype=Magic.DataType)
        yy = y - c * np.sin(theta)
        d = np.sqrt(xx * xx + yy * yy)
        if d > (a + b) or d < abs(a - b):
            return []
        q = np.arctan2(yy, xx)
        if d == (a + b):
            return [State(*wrap_to_pi([q, 0, theta - q])), ]
        if d == abs(a - b):
            return [State(*wrap_to_pi([q, np.pi, theta - q - np.pi])), ]

        tmp = (a * a + d * d - b * b) / (2 * a * d)
        q1 = -np.arccos(tmp) + q
        q12 = np.arccos(tmp) + q
        tmp = (a * a + b * b - d * d) / (2 * a * b)
        q2 = np.pi - np.arccos(tmp)
        return [State(*wrap_to_pi([q1, q2, theta - q1 - q2])), State(*wrap_to_pi([q12, -q2, theta - q12 + q2])), ]

    def fk(self, s: State) -> State:
        return State(
            0.5 * np.cos(s[0], dtype=Magic.DataType) + 0.4 * np.cos(s[0] + s[1], dtype=Magic.DataType) + 0.1 * np.cos(
                s[0] + s[1] + s[2], dtype=Magic.DataType),
            0.5 * np.sin(s[0], dtype=Magic.DataType) + 0.4 * np.sin(s[0] + s[1], dtype=Magic.DataType) + 0.1 * np.sin(
                s[0] + s[1] + s[2], dtype=Magic.DataType),
            s[0] + s[1] + s[2]
        )


class JakaSpace(Space):
    def __init__(self, lb: Tuple, ub: Tuple):
        super().__init__(lb, ub)
        self.check_validity_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)

    def check_validity(self, s: State) -> bool:
        req = moveit_msgs.srv.GetStateValidityRequest()
        req.group_name = 'arm'
        req.robot_state.joint_state.name = [f'right_joint_{i}' for i in range(1, 7)]
        req.robot_state.joint_state.position = s.data_view.tolist()
        resp: moveit_msgs.srv.GetStateValidityResponse = self.check_validity_srv.call(req)
        return resp.valid


class JakaDecomp(Decomposition):
    def __init__(self, lb: Tuple, ub: Tuple, slices: Tuple):
        super().__init__(lb, ub, slices)
        self.ik_srv = rospy.ServiceProxy("/compute_ik", moveit_msgs.srv.GetPositionIK)
        self.fk_srv = rospy.ServiceProxy("/compute_fk", moveit_msgs.srv.GetPositionFK)

    @staticmethod
    def _set_cell_free_vol(cells_dict: Dict[Tuple, Cell]):
        pass
        cells_dict[(8, 6, 8)].free_vol = 0.2

    def fk(self, s: State) -> State:
        req = moveit_msgs.srv.GetPositionFKRequest()
        req.robot_state.joint_state.name = [f'right_joint_{i}' for i in range(1, 7)]
        req.robot_state.joint_state.position = s.data_view.tolist()
        req.fk_link_names = ["right_gripper_base_link"]
        req.header.frame_id = "right_base_link"
        resp: moveit_msgs.srv.GetPositionFKResponse = self.fk_srv.call(req)
        pose_stamped: geometry_msgs.msg.PoseStamped = resp.pose_stamped[0]
        qua = pose_stamped.pose.orientation
        angles = tf.transformations.euler_from_quaternion([
            qua.x, qua.y, qua.z, qua.w
        ])
        return State(pose_stamped.pose.position.x, pose_stamped.pose.position.y, pose_stamped.pose.position.z, *angles)

    def _moveit_ik(self, w_s: State, seed: State) -> Union[State, None]:
        req = moveit_msgs.srv.GetPositionIKRequest()
        req.ik_request.group_name = 'arm'
        req.ik_request.robot_state.joint_state.name = [f'right_joint_{i}' for i in range(1, 7)]
        req.ik_request.robot_state.joint_state.position = seed.data_view.tolist()
        req.ik_request.ik_link_name = "right_gripper_base_link"
        req.ik_request.pose_stamped.header.frame_id = "right_base_link"
        req.ik_request.timeout = rospy.Duration.from_sec(1.0)
        req.ik_request.pose_stamped.pose.position.x = w_s[0]
        req.ik_request.pose_stamped.pose.position.y = w_s[1]
        req.ik_request.pose_stamped.pose.position.z = w_s[2]
        qua = tf.transformations.quaternion_from_euler(w_s[3], w_s[4], w_s[5], 'sxyz')
        req.ik_request.pose_stamped.pose.orientation.x = qua[0]
        req.ik_request.pose_stamped.pose.orientation.y = qua[1]
        req.ik_request.pose_stamped.pose.orientation.z = qua[2]
        req.ik_request.pose_stamped.pose.orientation.w = qua[3]
        resp: moveit_msgs.srv.GetPositionIKResponse = self.ik_srv.call(req)
        if resp.error_code.val == resp.error_code.SUCCESS:
            return State(*resp.solution.joint_state.position)

    def _sample_in_cell(self, cell: Cell, seed: Union[None, State]) -> Union[State, None]:
        pt = cell.ws.sample_uniform()
        if seed is not None and np.random.random() < 0.95:
            pt.data_view[3:] = self.fk(seed).data_view[3:]
        if seed is None:
            seed = State(*np.random.uniform(
                (-4.963716393, -1.171988593, -2.412917691, -1.171988593, -4.963716393, -4.963716393),
                (4.963716393, 3.653846789, 2.412917691, 3.653846789, 4.963716393, 4.963716393)
            ))

        return self._moveit_ik(pt, seed)


def planar():
    space = PlanarSpace((-np.pi, -np.pi, -np.pi), (np.pi, np.pi, np.pi))
    decomp = PlanarDecomp((-1.1, -1.1, -np.pi), (1.1, 1.1, np.pi), (9, 7))

    stp = STP(space, decomp)

    s1 = State(*np.deg2rad([0, 0, 30]))
    s2 = State(*np.deg2rad([120, -60, 30]))

    tot=np.linspace(0,0.9,10)
    f = open('/home/msi/compaglog.txt', 'w')
    for p1 in tot:
        for p2 in tot:
            stp.p1=p1
            stp.p2=p2

            t = time.time()
            res,count = stp.solve(s1, s2)
            cost = time.time() - t

            f.write(f"p1: {p1}  p2:{p2}  \n" )
            # print(f"count: {count:.2f}",file='~\\compaglog.txt')
            f.write(f"count: {count} \n")
            # print(f"res: {res}")
            f.write(f"cost: {cost * 1000.0:.2f} ms")
            f.write("\n")
            f.write("\n")
            f.write("\n")
            # print(f"cost: {cost * 1000.0:.2f} ms",file='~\\compaglog.txt')
    f.close


def jaka():
    # robot = moveit_commander.RobotCommander()
    # for joint_name in robot.get_joint_names('arm'):
    #     j: moveit_commander.RobotCommander.Joint = robot.get_joint(joint_name)
    #     # print(f"{joint_name}: {j.min_bound()} ~ {j.max_bound()}")
    #     print(f"{j.max_bound()}", end=', ')

    space = JakaSpace(
        (-4.963716393, -1.171988593, -2.412917691, -1.171988593, -4.963716393, -4.963716393),
        (4.963716393, 3.653846789, 2.412917691, 3.653846789, 4.963716393, 4.963716393)
    )
    decomp = JakaDecomp(
        (-1.0, -1.0, -1.0, -np.pi, -np.pi, -np.pi),
        (1.0, 1.0, 1.0, np.pi, np.pi, np.pi),
        (12, 12, 12)
    )

    stp = STP(space, decomp)

    s1 = State(*np.deg2rad([-30, 60, -45, -17, -115, 0]))
    s2 = State(*np.deg2rad([45, 60, -64, 20, -30, 0]))

    t = time.time()
    res = stp.solve(s1, s2)
    cost = time.time() - t
    print(f"res: {res}")
    print(f"cost: {cost * 1000.0:.2f} ms")


def plot():
    space = JakaSpace(
        (-4.963716393, -1.171988593, -2.412917691, -1.171988593, -4.963716393, -4.963716393),
        (4.963716393, 3.653846789, 2.412917691, 3.653846789, 4.963716393, 4.963716393)
    )
    decomp = JakaDecomp(
        (-1.0, -1.0, -1.0, -np.pi, -np.pi, -np.pi),
        (1.0, 1.0, 1.0, np.pi, np.pi, np.pi),
        (12, 12, 12)
    )

    stp = STP(space, decomp)

    s1 = State(*np.deg2rad([-30, 60, -45, -17, -115, 0]))
    s2 = State(*np.deg2rad([45, 60, -64, 20, -30, 0]))
    stp.plot2(s1, s2)
    # stp.plot3()


if __name__ == '__main__':
    rospy.init_node("main")
    planar()
    # jaka()
    # plot()
