#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/8 下午9:11
"""
from math import pi
import geometry_msgs.msg
import moveit_msgs.msg
import numpy as np
import yaml
from copy import deepcopy
from prettytable import PrettyTable
import tf.transformations
from typing import Union


class Constant:
    moveit_error_code_map = {
        moveit_msgs.msg.MoveItErrorCodes.SUCCESS: 'success',
        moveit_msgs.msg.MoveItErrorCodes.FAILURE: 'failure',
        moveit_msgs.msg.MoveItErrorCodes.PLANNING_FAILED: 'planning_failed',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_MOTION_PLAN: 'invalid_motion_plan',
        moveit_msgs.msg.MoveItErrorCodes.MOTION_PLAN_INVALIDATED_BY_ENVIRONMENT_CHANGE: 'motion_plan_invalidated_by_environment_change',
        moveit_msgs.msg.MoveItErrorCodes.CONTROL_FAILED: 'control_failed',
        moveit_msgs.msg.MoveItErrorCodes.UNABLE_TO_AQUIRE_SENSOR_DATA: 'unable_to_aquire_sensor_data',
        moveit_msgs.msg.MoveItErrorCodes.TIMED_OUT: 'timed_out',
        moveit_msgs.msg.MoveItErrorCodes.PREEMPTED: 'preempted',
        moveit_msgs.msg.MoveItErrorCodes.START_STATE_IN_COLLISION: 'start_state_in_collision',
        moveit_msgs.msg.MoveItErrorCodes.START_STATE_VIOLATES_PATH_CONSTRAINTS: 'start_state_violates_path_constraints',
        moveit_msgs.msg.MoveItErrorCodes.GOAL_IN_COLLISION: 'goal_in_collision',
        moveit_msgs.msg.MoveItErrorCodes.GOAL_VIOLATES_PATH_CONSTRAINTS: 'goal_violates_path_constraints',
        moveit_msgs.msg.MoveItErrorCodes.GOAL_CONSTRAINTS_VIOLATED: 'goal_constraints_violated',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_GROUP_NAME: 'invalid_group_name',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_GOAL_CONSTRAINTS: 'invalid_goal_constraints',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_ROBOT_STATE: 'invalid_robot_state',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_LINK_NAME: 'invalid_link_name',
        moveit_msgs.msg.MoveItErrorCodes.INVALID_OBJECT_NAME: 'invalid_object_name',
        moveit_msgs.msg.MoveItErrorCodes.FRAME_TRANSFORM_FAILURE: 'frame_transform_failure',
        moveit_msgs.msg.MoveItErrorCodes.COLLISION_CHECKING_UNAVAILABLE: 'collision_checking_unavailable',
        moveit_msgs.msg.MoveItErrorCodes.ROBOT_STATE_STALE: 'robot_state_stale',
        moveit_msgs.msg.MoveItErrorCodes.SENSOR_INFO_STALE: 'sensor_info_stale',
        moveit_msgs.msg.MoveItErrorCodes.COMMUNICATION_FAILURE: 'communication_failure',
        moveit_msgs.msg.MoveItErrorCodes.NO_IK_SOLUTION: 'no_ik_solution'
    }


def rad2deg(rad: Union[float, list, dict]) -> Union[float, list, dict]:
    if isinstance(rad, list) or isinstance(rad, tuple):
        return [val / pi * 180 for val in rad]
    elif isinstance(rad, dict):
        tmp = {}
        for key in rad:
            tmp[key] = rad[key] / pi * 180
        return tmp
    else:
        return rad / pi * 180


def deg2rad(deg: Union[float, list, dict]) -> Union[float, list, dict]:
    if isinstance(deg, list) or isinstance(deg, tuple):
        return [val / 180 * pi for val in deg]
    elif isinstance(deg, dict):
        tmp = {}
        for key in deg:
            tmp[key] = deg[key] / 180 * pi
        return tmp
    else:
        return deg / 180 * pi


def wrap2pi(rad: float or list) -> float or list:
    if isinstance(rad, list) or isinstance(rad, tuple):
        return [wrap2pi(val) for val in rad]
    else:
        return (rad + pi) % (2 * pi) - pi


# def combine_dicts(*args) -> dict:
#     res = {}
#     for d in args:
#         res.update(d)
#     return res


def j_val_to_state(j_vals) -> moveit_msgs.msg.RobotState:
    msg = moveit_msgs.msg.RobotState()
    msg.joint_state.name = ['left_joint_%d' % i for i in range(1, 7)]
    msg.joint_state.name.extend(['right_joint_%d' % i for i in range(1, 7)])
    msg.joint_state.position = j_vals
    return msg

def moveit_error_code_to_string(error_code: moveit_msgs.msg.MoveItErrorCodes) -> str:
    if error_code.val not in Constant.moveit_error_code_map:
        return 'unknown error'
    return Constant.moveit_error_code_map[error_code.val]


def get_config_from_state(prefix_list: list, robot_state: moveit_msgs.msg.RobotState):
    assert isinstance(prefix_list, list)
    n = len(robot_state.joint_state.name)
    ans = []
    for p in prefix_list:
        for i in range(n):
            name = robot_state.joint_state.name[i]
            if name.startswith(p) and 'finger' not in name:
                ans.append(robot_state.joint_state.position[i])
    return ans




class JointLimitsTool:
    def __init__(self):
        self.default_limits = {
            'left_joint_1': (360, -360),
            'left_joint_2': (265, -85),
            'left_joint_3': (175, -175),
            'left_joint_4': (265, -85),
            'left_joint_5': (360, -360),
            'left_joint_6': (360, -360),
            #
            'right_joint_1': (360, -360),
            'right_joint_2': (265, -85),
            'right_joint_3': (175, -175),
            'right_joint_4': (265, -85),
            'right_joint_5': (360, -360),
            'right_joint_6': (360, -360),
        }
        self.default_threshold = 0.85
        for key in self.default_limits:
            self.default_limits[key] = tuple(map(lambda x: deg2rad(x) * self.default_threshold,
                                                 self.default_limits[key]))
        self.custom_limits = {
        }
        self.filenames = "/home/msi/catkin_ws/src/dual_v45_moveit_config/config/joint_limits.yaml"
        self.max_acceleration = deg2rad(720)
        self.max_velocity = deg2rad(180)

    def overwrite(self):
        for key in self.custom_limits:
            if self.default_limits[key][0] >= self.custom_limits[key][0] >= self.default_limits[key][1] and \
                    self.default_limits[key][0] >= self.custom_limits[key][1] >= self.default_limits[key][1] and \
                    self.custom_limits[key][0] > self.custom_limits[key][1]:
                continue
            else:
                raise ValueError
        _d = deepcopy(self.default_limits)
        _d.update(self.custom_limits)
        self._write(_d)

    def _write(self, table):
        with open(self.filenames, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        for joint_name in table:
            data['joint_limits'][joint_name]['max_position'] = table[joint_name][0]
            data['joint_limits'][joint_name]['min_position'] = table[joint_name][1]
            data['joint_limits'][joint_name]['max_acceleration'] = self.max_acceleration
            data['joint_limits'][joint_name]['max_velocity'] = self.max_velocity
        with open(self.filenames, 'w') as f:
            yaml.dump(data, f)

    def print_current_config(self):
        with open(self.filenames, 'r') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        joint_limits = data['joint_limits']
        fields = ['max_position', 'min_position', 'max_velocity', 'max_acceleration']
        _table = PrettyTable(["joint_name", *fields])
        for joint_name in joint_limits:
            if 'finger' in joint_name:
                continue
            row = [joint_name]
            for field in fields:
                row.append("%.9f (%.f)" % (
                    float(joint_limits[joint_name][field]), rad2deg(float(joint_limits[joint_name][field]))))
            _table.add_row(row)
        print(_table)

    def check_joint_default_limit(self, joints: dict):
        invalid_joints = []
        for joint_name in joints:
            if self.default_limits[joint_name][1] <= joints[joint_name] <= self.default_limits[joint_name][0]:
                continue
            else:
                invalid_joints.append(joint_name)
        return invalid_joints
