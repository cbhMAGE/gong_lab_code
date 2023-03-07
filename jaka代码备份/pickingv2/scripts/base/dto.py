#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/25 下午6:53
"""
import moveit_msgs.msg
import rospy
import tf.transformations
from copy import deepcopy
import numpy as np
import geometry_msgs.msg
from .tools import rad2deg, deg2rad
from typing import Union
from prettytable import PrettyTable
import trajectory_msgs.msg
import tf2_ros
import tf2_geometry_msgs
import threading


class Target:
    lock = threading.Lock()

    def __init__(self,  tform: 'Transform', frame_id: str):
        self._tform_dict = {
            frame_id: tform
        }
        self._name = ""
        self._pixel_center_pt = Point()
        self._configs = ([], [])
        self._is_finished = False
        self._desc = []
        with Target.lock:
            if not hasattr(Target, "_tf_buffer"):
                Target._tf_buffer = tf2_ros.Buffer()
                Target._tf_listener = tf2_ros.TransformListener(Target._tf_buffer)

    def set_name(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def set_tform(self, frame_id: str, tform: 'Transform'):
        self._tform_dict[frame_id] = tform.copy()

    def tform(self, target_frame: str) -> Union['Transform', None]:
        if target_frame in self._tform_dict:
            return self._tform_dict[target_frame].copy()
        for k in self._tform_dict:
            msg = self._tform_dict[k].to_msg_pose_stamped(k)
            msg.header.stamp = rospy.Time(0)
            rate = rospy.Rate(60)
            for i in range(10):
                try:
                    return Transform.build_from_pose_msg(
                        Target._tf_buffer.transform(msg, target_frame=target_frame, timeout=rospy.Duration(secs=1)))
                except (tf2_ros.LookupException, tf2_ros.ConnectivityException, tf2_ros.ExtrapolationException):
                    rate.sleep()
            rospy.logerr("tf transform is stuck here after 10 attempts...")
            return None

    # def to_msg_pose_stamped(self) -> geometry_msgs.msg.PoseStamped:
    #     return self._tform.to_msg_pose_stamped(self._frame_id)

    def set_configs(self, l_configs, r_configs):
        self._configs = (l_configs, r_configs)

    def set_finished(self):
        self.add_desc('finished')
        self._is_finished = True

    @property
    def is_finished(self) -> bool:
        return self._is_finished

    def add_desc(self, txt: str):
        self._desc.append(txt)

    @property
    def desc(self) -> str:
        return ', '.join(self._desc)


class RobotConfig:
    default_order = (
        'left_joint_1',
        'left_joint_2',
        'left_joint_3',
        'left_joint_4',
        'left_joint_5',
        'left_joint_6',
        'right_joint_1',
        'right_joint_2',
        'right_joint_3',
        'right_joint_4',
        'right_joint_5',
        'right_joint_6',
    )

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
            tmp[f'{prefix:s}joint_{idx + 1:d}'] = val
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
        array = []
        for k in self.default_order:
            if k in self._data:
                array.append(self._data[k])
        return array

    def to_robot_states(self) -> moveit_msgs.msg.RobotState:
        msg = moveit_msgs.msg.RobotState()
        msg.joint_state.name = self.get_names()
        msg.joint_state.position = self.to_array()
        return msg

    def to_trajectory_point(self, time_from_start: float) -> trajectory_msgs.msg.JointTrajectoryPoint:
        msg = trajectory_msgs.msg.JointTrajectoryPoint()
        msg.time_from_start = rospy.Duration.from_sec(time_from_start)
        msg.positions = self.to_array()
        return msg

    def update(self, other: 'RobotConfig') -> 'RobotConfig':
        d = self._data.copy()
        d.update(other.to_dict())
        return RobotConfig(d)

    def get_names(self) -> list:
        array = []
        for k in self.default_order:
            if k in self._data:
                array.append(k)
        return array

    def sub_config(self, prefix) -> 'RobotConfig':
        return RobotConfig(dict((k, self._data[k]) for k in self._data if prefix in k))

    def __add__(self, other: 'RobotConfig') -> 'RobotConfig':
        tmp = self._data.copy()
        tmp.update(other.to_dict())
        return RobotConfig(tmp)

    def __str__(self):
        t = PrettyTable(('j_name', 'deg'))
        for k in self._data:
            t.add_row((k, rad2deg(self._data[k])))
        t.align['deg'] = 'r'
        return str(t)

    def __repr__(self):
        return self.__str__()


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
    
    def length(self)->float:
        return np.linalg.norm(self._xyz)

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
