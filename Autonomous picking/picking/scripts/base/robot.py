#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/11 下午9:59
"""
import threading

import moveit_commander
import std_msgs.msg
import trajectory_msgs.msg

from ik import AnalyticalIK
import rospy
import moveit_msgs.srv
from tools import deg2rad, rad2deg
from typing import List, Union
import numpy as np
from dto import Transform, Point, Euler, RobotConfig

from tools import moveit_error_code_to_string, j_val_to_state
import visualization_msgs.msg
import geometry_msgs.msg
from copy import deepcopy
import tf2_ros
import tf2_geometry_msgs
import moveit_msgs.msg

np.set_printoptions(suppress=True)


class RvizTool:
    line_list_marker_id = 3

    color_red_msg = std_msgs.msg.ColorRGBA(1, 0, 0, 1)
    color_green_msg = std_msgs.msg.ColorRGBA(0, 1, 0, 1)
    color_blue_msg = std_msgs.msg.ColorRGBA(0.2, 0.3, 1, 1)

    def __init__(self):
        self.marker_pub = rospy.Publisher('/yzy_rviz_visual', visualization_msgs.msg.Marker, queue_size=10, latch=True)
        self.pose_array_pub = (rospy.Publisher('/yzy_grasp_path_left', geometry_msgs.msg.PoseArray, queue_size=10, latch=True),
                               rospy.Publisher('/yzy_grasp_path_right', geometry_msgs.msg.PoseArray, queue_size=10, latch=True))

        self.tarj_pub = rospy.Publisher('yzy_display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=10)
        rospy.sleep(0.5)
        self.wireframe_cuboid_msg = self._gen_wireframe_cuboid_msg()

    @staticmethod
    def _gen_wireframe_cuboid_msg():
        msg = visualization_msgs.msg.Marker()
        msg.header.frame_id = "platform"
        msg.type = visualization_msgs.msg.Marker.LINE_LIST
        msg.action = visualization_msgs.msg.Marker.ADD
        msg.scale = geometry_msgs.msg.Vector3(0.005, 0.005, 0.005)
        color_msg = std_msgs.msg.ColorRGBA(0.1, 0.9, 0.3, 1.0)
        msg.color = color_msg
        size = 0.05
        # axes
        c_pts = [Point(0, 0, 0), Point(1, 0, 0), Point(0, 0, 0), Point(0, 1, 0), Point(0, 0, 0), Point(0, 0, 1)]
        msg.points = [p * size for p in c_pts]
        msg.colors = [RvizTool.color_red_msg, RvizTool.color_red_msg,
                      RvizTool.color_green_msg, RvizTool.color_green_msg,
                      RvizTool.color_blue_msg, RvizTool.color_blue_msg]
        # box
        pts = [Point(1, 1, -1), Point(1, -1, -1), Point(-1, -1, -1), Point(-1, 1, -1),
               Point(1, 1, 1), Point(1, -1, 1), Point(-1, -1, 1), Point(-1, 1, 1)]
        pts = [p * size for p in pts]
        msg.points.extend(pts)
        msg.points.extend([pts[i + v] for i in range(4) for v in (0, 4)])
        msg.points.extend([pts[3], pts[0], pts[1], pts[2], pts[7], pts[4], pts[5], pts[6]])
        msg.colors.extend([color_msg for _ in range(24)])

        msg.points = [p.to_msg_point() for p in msg.points]
        msg.lifetime = rospy.Duration(0)
        return msg

    def publish_wireframe_cuboid(self, tform: Transform):
        msg = deepcopy(self.wireframe_cuboid_msg)
        msg.header.stamp = rospy.Time.now()
        msg.pose = tform.to_msg_pose()
        msg.id = self.line_list_marker_id
        self.marker_pub.publish(msg)
        self.line_list_marker_id += 1

    def publish_grasp_path(self, tfs: List[Transform], frame_id: str, idx=0):
        msg = geometry_msgs.msg.PoseArray()
        msg.header.frame_id = frame_id
        msg.poses = [_tf.to_msg_pose() for _tf in tfs]
        self.pose_array_pub[idx].publish(msg)

    def publish_planned_path(self, start_state, lr_trajs: List[List]):
        msg = moveit_msgs.msg.DisplayTrajectory()
        msg.trajectory_start = start_state
        j_names = [f'left_joint_{i:d}' for i in range(1, 7)]
        j_names.extend([f'right_joint_{i:d}' for i in range(1, 7)])

        traj = moveit_msgs.msg.RobotTrajectory()
        traj.joint_trajectory.joint_names = j_names
        for i in range(len(lr_trajs[0])):
            jtp = trajectory_msgs.msg.JointTrajectoryPoint()
            jtp.positions = deepcopy(lr_trajs[0][i])
            jtp.positions.extend(deepcopy(lr_trajs[1][i]))
            traj.joint_trajectory.points.append(jtp)
        msg.trajectory = [traj]
        self.tarj_pub.publish(msg)


class Target:
    lock = threading.Lock()

    def __init__(self, tform: Transform, frame_id: str):
        self._tform = tform
        self._frame_id = frame_id
        self._configs = ([], [])
        self._is_finished = False
        self._desc = []

    @property
    def frame_id(self) -> str:
        return self._frame_id

    def tform(self, target_frame=None) -> Union[Transform, None]:
        if target_frame == self._frame_id or target_frame is None:
            return self._tform.copy()
        with Target.lock:
            if not hasattr(Target, "_tf_buffer"):
                Target._tf_buffer = tf2_ros.Buffer()
                Target._tf_listener = tf2_ros.TransformListener(Target._tf_buffer)
        msg = self._tform.to_msg_pose_stamped(self._frame_id)
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

    def to_msg_pose_stamped(self) -> geometry_msgs.msg.PoseStamped:
        return self._tform.to_msg_pose_stamped(self._frame_id)

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


class Dual:
    def __init__(self):
        # analytical ik
        self.left_aik = AnalyticalIK(robot_type='zu7_v1')
        self.right_aik = AnalyticalIK(robot_type='zu7_v2')

        # tcp2end
        self.left_tcp2end = Point(0, 0, 0.1).to_tform()
        self.right_tcp2end = Point(0, 0, 0.1).to_tform()

        # home config
        self.left_home_config = RobotConfig.build_from_deg({
            'left_joint_1': -90,
            'left_joint_2': 90,
            'left_joint_3': -50,
            'left_joint_4': 200,
            'left_joint_5': 170,
            'left_joint_6': 0,
        })
        self.right_home_config = RobotConfig.build_from_deg({
            'right_joint_1': 90,
            'right_joint_2': 90,
            'right_joint_3': 60,
            'right_joint_4': -30,
            'right_joint_5': -170,
            'right_joint_6': 0,
        })
        self.dual_home_config = self.left_home_config + self.right_home_config

        # pick config
        self.left_place_config = RobotConfig.build_from_deg({
            'left_joint_1': -80,
            'left_joint_2': 90,
            'left_joint_3': -130,
            'left_joint_4': 150,
            'left_joint_5': 90,
            'left_joint_6': 0,
        })
        self.right_place_config = RobotConfig.build_from_deg({
            'right_joint_1': 90,
            'right_joint_2': 100,
            'right_joint_3': 120,
            'right_joint_4': 35,
            'right_joint_5': -105,
            'right_joint_6': 0,
        })
        self.dual_place_config = self.left_place_config + self.right_place_config

        # state valid checker
        self.state_valid_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)
        self.state_valid_srv.wait_for_service()

        self.state_valid_req = moveit_msgs.srv.GetStateValidityRequest()
        self.state_valid_req.robot_state.joint_state.name = self.dual_home_config.get_names()
        self.state_valid_req.group_name = 'dual_arm'

        # move group
        self.move_group = moveit_commander.MoveGroupCommander('dual_arm')
        # self.move_group.set_planning_time(30)
        # self.move_group.set_planner_id('BiTRRT')
        # self.move_group.set_num_planning_attempts(100)

        # scene
        self.scene = moveit_commander.PlanningSceneInterface()

        # visualization tool
        self.rt = RvizTool()

    def _check_state_valid(self, l_config: list, r_config: list) -> bool:
        self.state_valid_req.robot_state.joint_state.position = deepcopy(l_config)
        self.state_valid_req.robot_state.joint_state.position.extend(r_config)
        # todo: add attached_collision_objects
        # self.state_valid_req.robot_state.attached_collision_objects = []
        resp: moveit_msgs.srv.GetStateValidityResponse = self.state_valid_srv(self.state_valid_req)
        return resp.valid

    @staticmethod
    def _extra_r_joint_limit(config) -> bool:
        if not (20 < rad2deg(config[0]) < 170.0):
            return False
        if not (10 < rad2deg(config[1]) < 170.0):
            return False
        if rad2deg(config[2]) < -5:
            return False
        return True

    @staticmethod
    def _extra_l_joint_limit(config) -> bool:
        if not (-170 < rad2deg(config[0]) < -20.0):
            return False
        if not (10 < rad2deg(config[1]) < 170.0):
            return False
        if rad2deg(config[2]) > 5:
            return False
        return True

    def _plan(self, start_state: moveit_msgs.msg.RobotState, goal_config: dict):
        self.move_group.set_start_state(start_state)
        self.move_group.set_joint_value_target(goal_config)
        success, plan, planning_time, error_code = self.move_group.plan()
        return success, plan, error_code

    def plan_home(self):
        start_state = self.move_group.get_current_state()
        return self._plan(start_state, self.dual_home_config.to_dict())

    # def _add_collision(self, l_target: Target, r_target: Target):
    #     tmp: Point = l_target.tform() * Point(0, 0, 0.12)
    #     msg = l_target.to_msg_pose_stamped()
    #     msg.pose.position = tmp.to_msg_point()
    #     self.scene.add_sphere("l", msg, radius=0.03)
    #
    #     # tmp: Transform = l_target.tform() * Euler.build_from_deg(0, 90, 0).to_tform()
    #     # msg = l_target.to_msg_pose_stamped()
    #     # msg.pose = tmp.to_msg_pose()
    #     # msg.pose.position.z += 0.1
    #     # self.scene.add_cylinder("l2", msg, height=0.3, radius=0.005)
    #     # msg = deepcopy(msg)
    #     # msg.pose.position.z -= 0.2
    #     # self.scene.add_cylinder("l3", msg, height=0.3, radius=0.005)
    #     #
    #     # tmp: Transform = l_target.tform() * Euler.build_from_deg(90, 0, 0).to_tform()
    #     # msg = l_target.to_msg_pose_stamped()
    #     # msg.pose = tmp.to_msg_pose()
    #     # msg.pose.position.x += 0.1
    #     # msg.pose.position.y -= 0.02
    #     # self.scene.add_cylinder("l4", msg, height=0.3, radius=0.005)
    #     # msg = deepcopy(msg)
    #     # msg.pose.position.x -= 0.2
    #     # self.scene.add_cylinder("l5", msg, height=0.3, radius=0.005)
    #
    #     # self.scene.add_mesh("l", tform.to_msg_pose_stamped(l_target.frame_id),
    #     #                     "/home/msi/1008_catkin_ws/src/picking/scripts/data/t0.obj")
    #     # self.scene.add_mesh("r", r_target.tform(), "")
    #     # self.scene.remove_world_object("l")
    #     # self.scene.remove_world_object("r")
    #     rospy.sleep(1)
    #     print(self.scene.get_known_object_names())

    @staticmethod
    def _gen_cartesian_path(tp: Point, num=20) -> List[Transform]:
        """
        from target_point to pre_pick position
        :param tp:
        :return:
        """
        dy = 0.15
        dz = 0.03
        degree = 1.5
        k = dz / (dy ** degree)
        ys = np.linspace(0, dy, num, endpoint=True)
        zs = k * np.power(ys, degree)
        phis = np.arctan(degree * k * np.power(ys, degree - 1))
        ys -= dy
        zs -= dz
        tfs = []
        for i in range(num):
            tfs.append(Transform.build_from_euler_point(
                Euler.build_from_deg(90 - rad2deg(phis[i]), 0, 0), tp + Point(0, -ys[i], zs[i])))
        # todo: add rotate operation
        return tfs[::-1]

    def _get_dual_target_config(self, l_t: Target, r_t: Target) -> RobotConfig or None:
        l_sols = self.left_aik.solve(l_t.tform('left_base_link'), tcp2end=self.left_tcp2end)
        l_sols = [sol for sol in l_sols if self._extra_l_joint_limit(sol)]

        r_sols = self.right_aik.solve(r_t.tform('right_base_link'), tcp2end=self.right_tcp2end)
        r_sols = [sol for sol in r_sols if self._extra_r_joint_limit(sol)]

        print(f"l_sols: {len(l_sols):d} r_sols: {len(r_sols):d}")
        r_sols.sort(key=lambda _: abs(_[4]))
        l_sols.sort(key=lambda _: abs(_[4]))
        print("l")
        for sol in l_sols:
            print(rad2deg(sol))
        print("r")
        for sol in r_sols:
            print(rad2deg(sol))

        combined = []
        for i_r in range(len(r_sols)):
            for i_l in range(len(l_sols)):
                combined.append((l_sols[i_l], r_sols[i_r], i_r + i_l))
        combined.sort(key=lambda _: _[-1])
        for _sols in combined:
            if self._check_state_valid(_sols[0], _sols[1]):
                return RobotConfig.build_from_jvals(_sols[0], 'left_') + RobotConfig.build_from_jvals(_sols[1], 'right_')
        return None

    def _try_dual_targets(self, l_tfs: List[Transform], r_tfs: List[Transform], start_state: moveit_msgs.msg.RobotState):
        c = self._get_dual_target_config(Target(l_tfs[0], 'platform'), Target(r_tfs[0], 'platform'))
        if not c:
            return False
        prev = (c.sub_config('left_').to_array(), c.sub_config('right_').to_array())
        # print('prev', prev)
        # print('prev_0 deg', rad2deg(prev[0]))
        # print('prev_1 deg', rad2deg(prev[1]))

        traj: List[RobotConfig] = []
        dual_path_valid = True
        for idx in range(1, len(l_tfs)):
            _l, max_jump_l = self.left_aik.solve(Target(l_tfs[idx], 'platform').tform('left_base_link'), seed=prev[0],
                                                 tcp2end=self.left_tcp2end, seed_threshold_deg=12)
            _r, max_jump_r = self.right_aik.solve(Target(r_tfs[idx], 'platform').tform('right_base_link'), seed=prev[1],
                                                  tcp2end=self.right_tcp2end, seed_threshold_deg=12)
            rospy.loginfo(f'{idx}: {rad2deg(max_jump_l)} {rad2deg(max_jump_r)}')
            if _l and _r and self._check_state_valid(_l[0], _r[0]):
                prev = (_l[0], _r[0])
                traj.append(
                    RobotConfig.build_from_jvals(_l[0], 'left_') + RobotConfig.build_from_jvals(_r[0], 'right_'))
            else:
                rospy.logwarn(f'[_try_dual_targets] find invalid pt at {idx}')
                dual_path_valid = False
                break
        if dual_path_valid:
            rospy.loginfo(f'[_try_dual_targets] grasp cartesian path valid')
            print(rad2deg(traj[-1].to_dict()))
            s, p, e = self._plan(start_state, traj[-1].to_dict())
            if s:
                return True
        return False

    def _try_single_target(self, tfs: List[Transform], prefix: str, start_state: moveit_msgs.msg.RobotState) -> bool:
        aik = self.left_aik if 'left' in prefix else self.right_aik
        tcp2end = self.left_tcp2end if 'left' in prefix else self.right_tcp2end
        sols = aik.solve(Target(tfs[0], 'platform').tform(f'{prefix:s}base_link'), tcp2end=tcp2end)
        if not sols:
            rospy.logwarn(f'[_try_single_target] cannot find sols')
            return False
        extra_joint_limit = self._extra_l_joint_limit if 'left' in prefix else self._extra_r_joint_limit
        sols = [sol for sol in sols if extra_joint_limit(sol)]
        sols.sort(key=lambda _: abs(_[4]))

        other_config = RobotConfig.build_from_robot_state(start_state, 'right_' if 'left' in prefix else 'left_')
        other_config_array = other_config.to_array()

        traj: List[RobotConfig] = []
        prev = sols[0]
        _path_valid = True
        for idx in range(1, len(tfs)):
            _s, max_jump = aik.solve(Target(tfs[idx], 'platform').tform(f'{prefix:s}base_link'), seed=prev,
                                     tcp2end=tcp2end, seed_threshold_deg=12)
            cs = (_s[0], other_config_array) if 'left' in prefix else (other_config_array, _s[0])
            if _s and self._check_state_valid(*cs):
                prev = _s[0]
                traj.append(
                    RobotConfig.build_from_jvals(_s[0], prefix) + other_config)
            else:
                rospy.logwarn(f'[_try_single_target] find invalid pt at {idx}')
                _path_valid = False
                break
        if _path_valid:
            rospy.loginfo(f'[_try_single_target] grasp cartesian path valid')
            print(rad2deg(traj[-1].to_dict()))
            s, p, e = self._plan(start_state, traj[-1].to_dict())
            s, p, e = self._plan(j_val_to_state(traj[-1].to_array()), )
            if s:
                return True
        return False

    def plan_picking(self, targets: List[Target]):
        targets.sort(key=lambda _t: -_t.tform(target_frame='platform').to_point().x)
        targets_num = len(targets)
        start_state = self.move_group.get_current_state()
        waypoint_num = 15

        l_tfs = []
        r_tfs = []
        for t in targets:
            l_tfs.append(self._gen_cartesian_path(t.tform(target_frame='platform').to_point(), num=waypoint_num))
            r_tfs.append(self._gen_cartesian_path(t.tform(target_frame='platform').to_point(), num=waypoint_num))
        for i in range(targets_num):
            for j in range(i + 1, targets_num):
                ret = self._try_dual_targets(l_tfs[i], r_tfs[j], start_state)
                if ret:
                    targets[i].set_finished()
                    targets[j].set_finished()
                    rospy.loginfo(f'grasp sol found {i} & {j}')
            if not targets[i].is_finished:
                ret = self._try_single_target(l_tfs[i], 'left_', start_state)
                if ret:
                    targets[i].set_finished()

        for i in range(targets_num):
            if not targets[i].is_finished:
                ret = self._try_single_target(r_tfs[i], 'right_', start_state)
                if ret:
                    targets[i].set_finished()
        rospy.loginfo('plan_picking finished.')


def t0():
    dual = Dual()
    s, p, e = dual.plan_home()
    print(s)
    print(moveit_error_code_to_string(e))


def t1():
    rt = RvizTool()
    rt.publish_wireframe_cuboid(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.3, -0.5, 0.5)))
    # rt.publish_grid(Point(0, 0, 0), Point(1, -1, 1))


def t2():
    rt = RvizTool()
    dual = Dual()
    ts = [
        Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.8, -0.3, 0.45)), 'platform'),
        Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.3, -2.3, 0.35)), 'platform'),
    ]
    for t in ts:
        rt.publish_wireframe_cuboid(t.tform())
    rospy.sleep(1)
    dual.plan_picking(ts)
    # print(moveit_error_code_to_string(e))


def t4():
    mg = moveit_commander.MoveGroupCommander('dual_arm')
    print(mg.get_current_state())


if __name__ == '__main__':
    np.set_printoptions(suppress=True, precision=3)
    rospy.init_node("robot_test", anonymous=True)

    t2()
    # rospy.spin()
    r = rospy.Rate(15)
    while not rospy.is_shutdown():
        r.sleep()

    #
    # robot.solve_collision_free_ik([
    #     [0.7491787432529773, -0.4327137888816126, 0.5014877740978422, 0.43836426585451166],
    #     [0.4344323413247334, -0.2505167064968258, -0.8651646782995094, 0.26059546857554794],
    #     [0.49999975146893794, 0.8660254942423476, 0.00030307309016846336, 0.3943727104995802],
    #     [0.0, 0.0, 0.0, 1.0],
    # ])
