#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/13 下午7:11
"""
import moveit_msgs.msg
import rospy
import tf.transformations
from copy import deepcopy
import numpy as np
import geometry_msgs.msg
from tools import rad2deg, deg2rad
from typing import Union
from prettytable import PrettyTable


# class Angle:
#     def __init__(self, rad=0.0):
#         self._rad = np.float64(rad)
#         self._sync_deg()
#
#     def _sync_deg(self):
#         self._deg = self._rad / np.pi * 180.0
#
#     @staticmethod
#     def build_from_deg(deg):
#         return Angle(deg / 180.0 * np.pi)
#
#     @staticmethod
#     def build_from_rad(rad):
#         return Angle(rad)
#
#     @property
#     def deg(self):
#         return self._deg
#
#     @property
#     def rad(self):
#         return self._rad
#
#     def __add__(self, other: 'Angle') -> 'Angle':
#         return Angle(self._rad + other.rad)
#
#     def __iadd__(self, other: 'Angle') -> 'Angle':
#         return Angle(self._rad + other.rad)
#
#     def __sub__(self, other: 'Angle') -> 'Angle':
#         return Angle(self._rad - other.rad)
#
#     def __isub__(self, other: 'Angle') -> 'Angle':
#         return Angle(self._rad - other.rad)
#
#     def __mul__(self, other: float) -> 'Angle':
#         return Angle(self._rad * other)
#
#     def __imul__(self, other: float) -> 'Angle':
#         return Angle(self._rad * other)
#
#     def __eq__(self, other: 'Angle') -> bool:
#         return self._rad == other.rad
#
#     def __ne__(self, other: 'Angle') -> bool:
#         return self._rad != other.rad
#
#     def __lt__(self, other: 'Angle') -> bool:
#         return self._rad < other.rad
#
#     def __gt__(self, other: 'Angle') -> bool:
#         return self._rad > other.rad
#
#     def __le__(self, other: 'Angle') -> bool:
#         return self._rad <= other.rad
#
#     def __ge__(self, other: 'Angle') -> bool:
#         return self._rad >= other.rad
#
#     def __repr__(self) -> str:
#         return '%.2f (deg)' % self._deg
#
#     def __str__(self) -> str:
#         return '%.2f (deg)' % self._deg
#
#     def wrap2pi(self):
#         self._rad = (self._rad + np.pi) % (2 * np.pi) - np.pi
#         self._sync_deg()


class Quaternion:
    def __init__(self, x=0.0, y=0.0, z=0.0, w=1.0):
        self._qua = np.array((x, y, z, w), dtype=np.double)

    @staticmethod
    def build_from_euler(euler: 'Euler') -> 'Quaternion':
        return Quaternion(*tf.transformations.quaternion_from_euler(euler.ai, euler.aj, euler.ak, euler.axes))

    @staticmethod
    def build_from_qua_msg(msg: geometry_msgs.msg.Quaternion) -> 'Quaternion':
        return Quaternion(msg.x, msg.y, msg.z, msg.w)

    def to_euler(self) -> 'Euler':
        return Euler(*tf.transformations.euler_from_quaternion(self._qua))

    def to_list(self):
        return deepcopy(list(self._qua))

    def to_msg_quaternion(self) -> geometry_msgs.msg.Quaternion:
        msg = geometry_msgs.msg.Quaternion()
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        msg.w = self.w
        return msg

    @property
    def x(self):
        return self._qua[0]

    @property
    def y(self):
        return self._qua[1]

    @property
    def z(self):
        return self._qua[2]

    @property
    def w(self):
        return self._qua[3]

    def to_mat4x4(self) -> np.ndarray:
        return tf.transformations.quaternion_matrix(self._qua)

    def __str__(self):
        return f'Qua({self.x:.4f}, {self.y:.4f}, {self.z:.4f}, {self.w:.4f})'

    def __repr__(self):
        return self.__str__()


class Euler:
    def __init__(self, ai=0.0, aj=0.0, ak=0.0, axes='sxyz'):
        self._euler = np.array((ai, aj, ak), dtype=np.double)
        self._axes = axes

    @staticmethod
    def build_from_qua(qua: Quaternion):
        return Euler(*tf.transformations.euler_from_quaternion(qua.to_list()))

    @staticmethod
    def build_from_tf_mat(tform: 'Transform'):
        return Euler(*tf.transformations.euler_from_matrix(tform.to_mat4x4()))

    @staticmethod
    def build_from_deg(rx, ry, rz):
        return Euler(rx / 180.0 * np.pi, ry / 180.0 * np.pi, rz / 180.0 * np.pi)

    def to_tform(self) -> 'Transform':
        return Transform(self.to_mat4x4())

    def to_qua(self):
        return Quaternion(*tf.transformations.quaternion_from_euler(*self._euler, axes=self._axes))

    def to_mat4x4(self) -> np.ndarray:
        return tf.transformations.euler_matrix(*self._euler, axes=self._axes)

    @property
    def ai(self) -> np.double:
        return self._euler[0]

    @property
    def aj(self) -> np.double:
        return self._euler[1]

    @property
    def ak(self) -> np.double:
        return self._euler[2]

    @property
    def axes(self):
        return self._axes

    def __str__(self):
        tmp = rad2deg(self._euler)
        return f'Euler({tmp[0]:.3f}, {tmp[1]:.3f}, {tmp[2]:.3f})(deg)'

    def __repr__(self):
        return self.__str__()


# class Translation:
#     def __init__(self, x=0.0, y=0.0, z=0.0):
#         self._vec = np.array((x, y, z), dtype=np.double)
#
#     def to_list(self) -> list:
#         return list(self._vec)
#
#     def __add__(self, other: 'Translation') -> 'Translation':
#         return Translation(self._vec[0] + other.x, self._vec[1] + other.y, self._vec[2] + other.z)
#
#     def __sub__(self, other: 'Translation') -> 'Translation':
#         return Translation(self._vec[0] - other.x, self._vec[1] - other.y, self._vec[2] - other.z)
#
#     @property
#     def x(self) -> np.double:
#         return self._vec[0]
#
#     @property
#     def y(self) -> np.double:
#         return self._vec[1]
#
#     @property
#     def z(self) -> np.double:
#         return self._vec[2]
#
#     def to_tform(self) -> 'Transform':
#         return Transform(self.to_mat4x4())
#
#     def to_msg_point(self) -> geometry_msgs.msg.Point:
#         msg = geometry_msgs.msg.Point()
#         msg.x = self.x
#         msg.y = self.y
#         msg.z = self.z
#         return msg
#
#     def to_mat4x4(self) -> np.ndarray:
#         mat = np.eye(4, dtype=np.double)
#         mat[:3, -1] = self._vec
#         return mat
#
#     def __str__(self) -> str:
#         return f'Trans({self.x:.3f}, {self.y:.3f}, {self.z:.3f})'
#
#     def __repr__(self) -> str:
#         return self.__str__()


class Point:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self._xyz = np.array((x, y, z), dtype=np.double)

    @staticmethod
    def build_from_homo(homo: np.ndarray):
        return Point(*homo.reshape(-1)[:3])

    @property
    def x(self) -> np.double:
        return self._xyz[0]

    @property
    def y(self) -> np.double:
        return self._xyz[1]

    @property
    def z(self) -> np.double:
        return self._xyz[2]

    def to_homo(self) -> np.ndarray:
        return np.append(self._xyz, 1).reshape((4, 1))

    def to_mat4x4(self) -> np.ndarray:
        mat = np.eye(4, dtype=np.double)
        mat[:3, -1] = self._xyz
        return mat

    def to_tform(self) -> 'Transform':
        return Transform(self.to_mat4x4())

    def to_msg_point(self) -> geometry_msgs.msg.Point:
        msg = geometry_msgs.msg.Point()
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        return msg

    def __getitem__(self, index: int) -> np.double:
        return self._xyz[index]

    def __str__(self):
        return f'Point({self.x:.3f}, {self.y:.3f}, {self.z:.3f})'

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other) -> 'Point':
        if isinstance(other, float):
            tmp = self._xyz * other
            return Point(*tmp)
        else:
            raise TypeError('a float is needed')

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)


class Transform:
    def __init__(self, mat=np.eye(4, dtype=np.double)):
        self._mat = np.array(mat).copy()

    @staticmethod
    def build_from_euler_point(euler: Euler, pt: Point) -> 'Transform':
        mat = euler.to_mat4x4()
        mat[:, -1] = pt.to_homo().reshape(-1)
        return Transform(mat)

    @staticmethod
    def build_from_qua_point(qua: Quaternion, pt: Point) -> 'Transform':
        mat = qua.to_mat4x4()
        mat[:, -1] = pt.to_homo().reshape(-1)
        return Transform(mat)

    @staticmethod
    def build_from_pose_msg(msg: Union[geometry_msgs.msg.Pose, geometry_msgs.msg.PoseStamped]) -> 'Transform':
        _p = msg
        if isinstance(msg, geometry_msgs.msg.PoseStamped):
            _p = msg.pose

        mat = Quaternion.build_from_qua_msg(_p.orientation).to_mat4x4()
        mat[0, -1] = _p.position.x
        mat[1, -1] = _p.position.y
        mat[2, -1] = _p.position.z
        return Transform(mat)

    def to_euler(self, axes='sxyz') -> Euler:
        return Euler(*tf.transformations.euler_from_matrix(self._mat), axes=axes)

    def to_qua(self) -> Quaternion:
        return Quaternion(*tf.transformations.quaternion_from_matrix(self._mat))

    def to_point(self) -> Point:
        return Point(*self._mat[:3, -1])

    def to_msg_pose_stamped(self, frame_id: str) -> geometry_msgs.msg.PoseStamped:
        msg = geometry_msgs.msg.PoseStamped()
        msg.header.stamp = rospy.Time.now()
        msg.header.frame_id = frame_id
        msg.pose = self.to_msg_pose()
        return msg

    def to_msg_pose(self) -> geometry_msgs.msg.Pose:
        msg = geometry_msgs.msg.Pose()
        msg.position = self.to_point().to_msg_point()
        msg.orientation = self.to_qua().to_msg_quaternion()
        return msg

    def to_mat4x4(self) -> np.ndarray:
        return self._mat.copy()

    def copy(self) -> 'Transform':
        return Transform(self._mat.copy())

    def offset(self, x=0.0, y=0.0, z=0.0) -> 'Transform':
        t: Point = self * Point(x, y, z)
        tmp = self._mat.copy()
        tmp[:, -1] = t.to_homo().reshape(-1)
        return Transform(tmp)

    def inv(self) -> 'Transform':
        return Transform(np.linalg.inv(self._mat))

    def __mul__(self, other: Union['Transform', Point]) -> Union['Transform', Point]:
        if isinstance(other, Transform):
            return Transform(np.matmul(self._mat, other.to_mat4x4()))
        elif isinstance(other, Point):
            return Point.build_from_homo(np.matmul(self._mat, other.to_homo()))
        else:
            raise TypeError('a Transform or Point is needed')

    def __str__(self):
        return str(self._mat)

    def __repr__(self):
        return self.__str__()


class RobotConfig:
    def __init__(self, c: dict):
        self._data = c.copy()

    @staticmethod
    def build_from_deg(c: dict) -> 'RobotConfig':
        return RobotConfig(deg2rad(c))

    @staticmethod
    def build_from_rad(c: dict) -> 'RobotConfig':
        return RobotConfig(c)

    @staticmethod
    def build_from_jvals(jvals: list, prefix: str) -> 'RobotConfig':
        tmp = {}
        for idx, val in enumerate(jvals):
            tmp[f'{prefix:s}joint_{idx+1:d}'] = val
        return RobotConfig(tmp)

    @staticmethod
    def build_from_robot_state(s: moveit_msgs.msg.RobotState, prefix='') -> 'RobotConfig':
        tmp = dict()
        for idx, k in enumerate(s.joint_state.name):
            if prefix in k:
                tmp[k] = s.joint_state.position[idx]
        return RobotConfig(tmp)

    def to_dict(self) -> dict:
        return self._data.copy()

    def to_array(self) -> list:
        return [self._data[k] for k in self._data]

    def get_names(self) -> list:
        return [k for k in self._data]

    def sub_config(self, prefix) -> 'RobotConfig':
        return RobotConfig(dict((k, self._data[k]) for k in self._data if prefix in k))

    def __add__(self, other: 'RobotConfig') -> 'RobotConfig':
        tmp = self._data.copy()
        tmp.update(other.to_dict())
        return RobotConfig(tmp)

    def __str__(self):
        t = PrettyTable(('j_name', 'deg'))
        for k in self._data:
            t.add_row((k, self._data[k]))
        t.align['deg'] = 'r'
        return str(t)

    def __repr__(self):
        return self.__str__()


if __name__ == '__main__':
    e = Euler(ai=deg2rad(30))
    print(e.to_qua())
    p = Point(10, 1, 1)
    print(e.to_tform() * p)

    print(RobotConfig({
        'left_joint_1': -90,
        'left_joint_2': 90,
        'left_joint_3': -50,
        'left_joint_4': 200,
        'left_joint_5': 170,
        'left_joint_6': 0,
    }))
