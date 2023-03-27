#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/11/9 下午3:15
"""
from .dto import RobotConfig, Point
from .tools import rad2deg, deg2rad
import yaml
from copy import deepcopy
from prettytable import PrettyTable
from typing import Dict, List


class Config:
    left_home_config = RobotConfig.build_from_deg({
        'left_joint_1': -90,
        'left_joint_2': 90,
        'left_joint_3': -50,
        'left_joint_4': 200,
        'left_joint_5': 170,
        'left_joint_6': 0,
    })
    right_home_config = RobotConfig.build_from_deg({
        'right_joint_1': 90,
        'right_joint_2': 90,
        'right_joint_3': 60,
        'right_joint_4': -30,
        'right_joint_5': -170,
        'right_joint_6': 0,
    })
    dual_home_config = left_home_config + right_home_config

    # pick config
    left_place_config = RobotConfig.build_from_deg({
        # 'left_joint_1': -90,
        # 'left_joint_2': 75,
        # 'left_joint_3': -119,
        # 'left_joint_4': 153,
        # 'left_joint_5': 90,
        # 'left_joint_6': 0,
        # -112.8, 113.5, -121.2, 97.3, 86.5, -15.1,
        # 'left_joint_1': -113,
        # 'left_joint_2': 113.5,
        # 'left_joint_3': -121,
        # 'left_joint_4': 97,
        # 'left_joint_5': 87,
        # 'left_joint_6': 0,
        #xxxxxx
        'left_joint_1': -93,
        'left_joint_2': 92,
        'left_joint_3': -117,
        'left_joint_4': 141.4,
        'left_joint_5': 97,
        'left_joint_6': 0,
    })
    right_place_config = RobotConfig.build_from_deg({
        # 'right_joint_1': 90,
        # 'right_joint_2': 100,
        # 'right_joint_3': 120,
        # 'right_joint_4': 35,
        # 'right_joint_5': -105,
        # 'right_joint_6': 0,
        # 60.7, 85.2, 124.9, 56.7, -91.2, 60.0,
        'right_joint_1': 60,
        'right_joint_2': 85,
        'right_joint_3': 125,
        'right_joint_4': 56,
        'right_joint_5': -91,
        'right_joint_6': 0,
    })
    dual_place_config = left_place_config + right_place_config

    # tcp2end
    left_tcp2end = Point(0, 0, 0.14).to_tform()
    right_tcp2end = Point(0, 0, 0.14).to_tform()


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
        self.default_threshold = 0.9
        for key in self.default_limits:
            self.default_limits[key] = tuple(map(lambda x: deg2rad(x) * self.default_threshold,
                                                 self.default_limits[key]))
        self.custom_limits = {
        }
        self.filenames = "/home/msi/1008_catkin_ws/src/dual_moveit_config/config/joint_limits.yaml"
        self.max_acceleration = deg2rad(720)
        self.max_velocity = deg2rad(180)

    def to_array(self, prefix: str) -> List:
        ans = []
        for key in self.default_limits:
            if prefix in key:
                ans.append(self.default_limits[key])
        return ans

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

    def check_joint_default_limit(self, joints: Dict):
        invalid_joints = []
        for joint_name in joints:
            if self.default_limits[joint_name][1] <= joints[joint_name] <= self.default_limits[joint_name][0]:
                continue
            else:
                invalid_joints.append(joint_name)
        return invalid_joints
