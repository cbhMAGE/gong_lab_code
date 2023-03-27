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

from base.dto import RobotConfig, Point, Transform, Euler, rad2deg, deg2rad, Target
from base.config import Config

import moveit_commander
from base.tools import moveit_error_code_to_string
from typing import List, Tuple, Union
from copy import deepcopy
from queue import Queue

from base.ik import AnalyticalIK
import moveit_msgs.srv
import visualization_msgs.msg
import std_msgs.msg
from base.cv import CV
from base.vehicle import Chassis, RELATIVE_MOTION
import pymoveit_core

blank_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
example_img = cv2.imread("/home/msi/Documents/data/div-rgb-png/0B_c.png")

np.set_printoptions(suppress=True)


class RvizTool:
    line_list_marker_id = 0

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

    def clear_wireframe_cuboid(self):
        msg = deepcopy(self.wireframe_cuboid_msg)
        msg.header.stamp = rospy.Time.now()
        msg.action = visualization_msgs.msg.Marker.DELETEALL
        self.marker_pub.publish(msg)
        self.line_list_marker_id = 0

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


class PickingSystem:
    _feedback = None #pickingv2.msg.PickingCmdFeedback()
    _result = None #pickingv2.msg.PickingCmdResult()

    _cmd_srv_name = "/picking/cmd"
    _control_srv_name = "/picking/control"
    _car_move_srv_name = "/picking/car_move"

    def __init__(self):
        # cmd
        self._cmd_srv = rospy.Service(self._cmd_srv_name, pickingv2.srv.PickingCmd, self._cmd_srv_cb)
        # control: stop or pause
        self._control_srv = rospy.Service(self._control_srv_name, pickingv2.srv.PickingControl, self._control_srv_cb)
        # car move
        self._car_move_srv = rospy.Service(self._car_move_srv_name, pickingv2.srv.CarMove, self._car_move_srv_cb)
        try:
            self.chassis = Chassis("/dev/ttyUSB0", 19200)
        except:
            rospy.logerr("[Chassis] Cannot open serial")
        #
        self._task = Task()

    def _car_move_srv_cb(self, req: pickingv2.srv.CarMoveRequest) -> pickingv2.srv.CarMoveResponse:
        rospy.loginfo(f'{self._car_move_srv_name:s}: receive {req.cmd} {req.distance:.2f}')
        resp = pickingv2.srv.CarMoveResponse()
        dis = req.distance
        if req.cmd == "backward":
            dis = -dis
        self.chassis.moveByDistance(RELATIVE_MOTION, round(dis * 50000.0))
        self.chassis.wait_for_complete()
        resp.success = True
        return resp

    # stop or pause
    def _control_srv_cb(self, req: pickingv2.srv.PickingControlRequest) -> pickingv2.srv.PickingControlResponse:
        rospy.loginfo(f'{self._control_srv_name:s}: receive {req.cmd}')
        resp = pickingv2.srv.PickingControlResponse()
        rospy.sleep(1)
        resp.success = True
        return resp

    def _cmd_srv_cb(self, req: pickingv2.srv.PickingCmdRequest) -> pickingv2.srv.PickingCmdResponse:
        rospy.loginfo(f'{self._cmd_srv_name:s}: receive {req.cmd}')
        resp = pickingv2.srv.PickingCmdResponse()
        # exec
        res = self._task.exec(req.cmd)
        resp.success = res['success']
        resp.desc = res['desc']
        return resp


class RobotClient:
    def __init__(self, dual_move_group: moveit_commander.MoveGroupCommander):
        self._dual_srv = rospy.ServiceProxy('/dual_trajectory_srv', qjaka_gui.srv.DualRobotJointMoveService)
        self._sample_srv = rospy.ServiceProxy('/picking/uniform_sample_filter', pickingv2.srv.PickingTrajectoryFilter)
        self._left_grasp_srv = rospy.ServiceProxy('left_grasp_srv', qjaka_gui.srv.GraspService)
        self._right_grasp_srv = rospy.ServiceProxy('right_grasp_srv', qjaka_gui.srv.GraspService)
        self._do_srv = rospy.ServiceProxy("digital_output_srv", qjaka_gui.srv.DigitalOutputService)

        self._default_order = (
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
        self.vel_scale = 0.5
        self.acc_scale = 0.5
        rospy.logwarn(f"vel: {self.vel_scale:.2f}, acc: {self.acc_scale:.2f}")
        self.dual_move_group = dual_move_group

    def dual_move(self, trajectories: List[moveit_msgs.msg.RobotTrajectory], prefix="") -> bool:
        trajectory = self._combine_plans(trajectories, self.dual_move_group)
        ret, t = self._sample(trajectory)
        if not ret:
            rospy.logerr("call sample filter failed in RobotClient.dual_move")
            return False
        req = qjaka_gui.srv.DualRobotJointMoveServiceRequest()
        req.max_buf = 25
        req.kp = 0.05
        req.kv = 0.1
        req.ka = 0.5
        req.step_num = 1
        req.enable_right = True
        req.enable_left = True
        if 'left_' in prefix:
            req.enable_right = False
        elif "right_" in prefix:
            req.enable_left = False
        req.left_joint_values, req.right_joint_values = self._trajectory_to_list(t)
        resp: qjaka_gui.srv.DualRobotJointMoveServiceResponse = self._dual_srv(req)
        print(resp)
        print(resp.left_desc.encode().decode())
        print(resp.right_desc.encode().decode())
        return resp.success

    def grasp(self, prefix):
        if prefix == 'dual':
            self.grasp_dual()
            return True
        else:
            try:
                req = qjaka_gui.srv.GraspServiceRequest()
                req.rotate_deg = 30
                req.rotate_vel_deg = 180
                req.rotate_acc_deg = 600
                grasp_srv = self._left_grasp_srv if 'left' in prefix else self._right_grasp_srv
                resp: qjaka_gui.srv.GraspServiceResponse = grasp_srv(req)
                if not resp.success:
                    print("grasp callback: ", resp.desc)
                    rospy.logerr("grasp failed")
                return resp.success
            except rospy.ServiceException as exc:
                print("Service did not process request: " + str(exc))
                return False

    def grasp_dual(self):
        t1 = threading.Thread(target=self.grasp, args=('left_',))
        t2 = threading.Thread(target=self.grasp, args=('right_',))
        t1.start()
        t2.start()
        if t1.is_alive():
            t1.join()
        if t2.is_alive():
            t2.join()

    def do(self, index: List[int], enable: List[bool]):
        try:
            req = qjaka_gui.srv.DigitalOutputServiceRequest(index=index, enable=enable)
            resp = self._do_srv(req)
            return True
        except rospy.ServiceException as exc:
            print("digital_output_srv did not process request: " + str(exc))
            return False

    def open_hand(self, prefix):
        if prefix == "right_":
            return self.do([0], [False])
        elif prefix == "left_":
            return self.do([1], [False])
        else:
            return self.do([0, 1], [False, False])

    def close_hand(self, prefix):
        if prefix == "right_":
            return self.do([0], [True])
        elif prefix == "left_":
            return self.do([1], [True])
        else:
            if self.do([0], [True]):
                return self.do([1], [True])
            return False

    def single_move(self, trajectories: List[moveit_msgs.msg.RobotTrajectory], prefix: str) -> bool:
        pass

    def _combine_plans(self, trajectories: List[moveit_msgs.msg.RobotTrajectory],
                       move_group: moveit_commander.MoveGroupCommander) -> moveit_msgs.msg.RobotTrajectory:
        msg = deepcopy(trajectories[0])
        prev_time = msg.joint_trajectory.points.__getitem__(-1).time_from_start.to_sec()
        new_pts = list(msg.joint_trajectory.points)
        for i in range(1, len(trajectories)):
            pts = deepcopy(trajectories[i].joint_trajectory.points)
            for p in pts:
                p.time_from_start = rospy.Duration.from_sec(prev_time + p.time_from_start.to_sec())
            new_pts.extend(pts)
        msg.joint_trajectory.points = new_pts

        # "time_optimal_trajectory_generation"
        # "iterative_spline_parameterization"
        # "iterative_time_parameterization"
        return move_group.retime_trajectory(
            move_group.get_current_state(), msg, velocity_scaling_factor=self.vel_scale,
            acceleration_scaling_factor=self.acc_scale,
            algorithm='time_optimal_trajectory_generation'
        )

    def _sample(self, trajectory_in):
        req = pickingv2.srv.PickingTrajectoryFilterRequest()
        req.trajectory = trajectory_in
        req.sample_duration = 0.008
        resp: pickingv2.srv.PickingTrajectoryFilterResponse = self._sample_srv(req)
        return resp.success, resp.trajectory

    def _trajectory_to_list(self, trajectory: moveit_msgs.msg.RobotTrajectory) -> list:
        pt_num = len(trajectory.joint_trajectory.points)
        res = []
        order = [trajectory.joint_trajectory.joint_names.index(name) for name in self._default_order if
                 name in trajectory.joint_trajectory.joint_names]
        if len(order) == 12:
            res.extend([[], []])
            for i in range(pt_num):
                pt: trajectory_msgs.msg.JointTrajectoryPoint = trajectory.joint_trajectory.points[i]
                for idx in order[:6]:
                    res[0].append(pt.positions[idx])
                for idx in order[6:]:
                    res[1].append(pt.positions[idx])
        elif len(order) == 6:
            for i in range(pt_num):
                pt: trajectory_msgs.msg.JointTrajectoryPoint = trajectory.joint_trajectory.points[i]
                for idx in order:
                    res.append(pt.positions[idx])
        else:
            raise IndexError
        return res


class TaskResult:
    def __init__(self, success: bool, desc: str, data=None):
        self._success = success
        self._desc = desc
        self._data = data

    def to_dict_response(self) -> dict:
        return {
            'success': self._success,
            'desc': self._desc,
        }

    @property
    def success(self) -> bool:
        return self._success

    @property
    def data(self) -> any:
        return self._data

    @staticmethod
    def no_such_cmd_response(cmd_name: str) -> dict:
        return {
            'success': False,
            'desc': f'no such cmd: {cmd_name}'
        }

    @staticmethod
    def task_busy_response() -> dict:
        return {
            'success': False,
            'desc': 'busy'
        }


class Task:
    def __init__(self):
        self._task_lock = threading.Lock()

        self._control_lock = threading.Lock()
        self._should_stop = False

        self.move_group = moveit_commander.MoveGroupCommander('dual_arm')
        self.single_move_group_dict = {
            "left_": moveit_commander.MoveGroupCommander('left_arm'),
            "right_": moveit_commander.MoveGroupCommander('right_arm'),
        }

        self._exec_funcs = {
            'go_home': self._go_home,
            'auto': self._auto,
            'pick': self._pick_task,
            "left_open_hand": self._hand_op(True, "left_"),
            "left_close_hand": self._hand_op(False, "left_"),
            "right_open_hand": self._hand_op(True, "right_"),
            "right_close_hand": self._hand_op(False, "right_"),
        }
        self._robot_client = RobotClient(dual_move_group=self.move_group)
        # analytical ik
        self.left_aik = AnalyticalIK(prefix="left_", robot_type='zu7_v1')
        self.right_aik = AnalyticalIK(prefix="right_", robot_type='zu7_v2')

        # state valid checker
        self.state_valid_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)
        self.state_valid_srv.wait_for_service()

        self.state_valid_req = moveit_msgs.srv.GetStateValidityRequest()
        self.state_valid_req.robot_state.joint_state.name = Config.dual_home_config.get_names()
        self.state_valid_req.group_name = 'dual_arm'

        self.rviz_tool = RvizTool()
        self._cv = CV()
        # detection result publisher
        self._detection_res_pub_name = "/picking/detection_result"
        self._detection_res_pub = rospy.Publisher(self._detection_res_pub_name, pickingv2.msg.DetectionResult, queue_size=3)
        self._bridge = cv_bridge.CvBridge()

    def publish_detection_result(self, img, ts: List[Target]):
        msg = pickingv2.msg.DetectionResult()
        msg.image = self._bridge.cv2_to_compressed_imgmsg(img)
        msg.pixel_pts_lt = [geometry_msgs.msg.Point(100, 200, 0), geometry_msgs.msg.Point(200, 300, 0)]
        msg.pixel_pts_rb = [geometry_msgs.msg.Point(120, 250, 0), geometry_msgs.msg.Point(280, 370, 0)]
        self._detection_res_pub.publish(msg)

    def exec(self, cmd_name: str):
        ret = self._task_lock.acquire(False)
        if ret:
            try:
                if cmd_name in self._exec_funcs:
                    result = self._exec_funcs[cmd_name]()
                    return result.to_dict_response()
                else:
                    return TaskResult.no_such_cmd_response(cmd_name)
            finally:
                self._task_lock.release()
        else:
            return TaskResult.task_busy_response()

    def stop(self):
        with self._control_lock:
            self._should_stop = True

    def _is_should_stop(self) -> bool:
        with self._control_lock:
            return self._should_stop

    def _hand_op(self, is_open: bool, prefix: str):
        def func():
            if is_open:
                self._robot_client.open_hand(prefix)
            else:
                self._robot_client.close_hand(prefix)
            return TaskResult(True, "")

        return func

    def _go_home(self) -> TaskResult:
        self.rviz_tool.clear_wireframe_cuboid()
        self.move_group.set_start_state_to_current_state()
        self.move_group.set_joint_value_target(Config.dual_home_config.to_dict())
        success, plan, planning_time, error_code = self.move_group.plan()
        if success:
            self._robot_client.dual_move([plan])
            pass
        return TaskResult(success, moveit_error_code_to_string(error_code), None)

    def _auto(self):
        self._pick_task()
        return TaskResult(True, "")

    def _detect(self) -> TaskResult:
        self.rviz_tool.clear_wireframe_cuboid()
        # ts = [
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.9, -0.1, 0.35)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.6, -0.11, 0.4)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.7, -0.23, 0.25)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.8, -0.3, 0.15)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.5, -0.25, 0.45)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.7, -0.3, 0.25)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.2, -0.25, 0.35)), 'platform'),
        #     Target(Transform.build_from_euler_point(Euler.build_from_deg(90, 0, 0), Point(0.1, -0.3, 0.3)), 'platform'),
        # ]

        ts, img_res = self._cv.get_cv_result()
        ts: List[Target] = ts
        self.publish_detection_result(img_res, ts)
        actual_ts = []
        for t in ts:
            tform = t.tform("platform")
            mat = tform.to_mat4x4()
            # print(mat)
            # mat[2, -1] += 0.1
            # print(mat)
            actual_ts.append(Target(Transform(mat), "platform"))
            self.rviz_tool.publish_wireframe_cuboid(tform)
        return TaskResult(True, "", actual_ts)

    def _pick_task(self):
        res = self._go_home()
        if not res.success:
            return res
        res = self._detect()
        if not res.success:
            return res
        ts: List[Target] = res.data
        q = Queue()
        # self._gen_paired_targets(ts, q)
        # self._exec_pick_place(q)
        t1 = threading.Thread(target=self._gen_paired_targets, args=(ts, q,))
        t2 = threading.Thread(target=self._exec_pick_place, args=(q,))
        t1.start()
        t2.start()
        if t1.is_alive():
            t1.join()
        if t2.is_alive():
            t2.join()

    @staticmethod
    def _gen_cartesian_path(tp: Point, num=20) -> List[Transform]:
        """
        from target_point to pre_pick position
        :param tp:
        :return:
        """
        # gripper distance
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

    def _get_dual_target_config(self, l_t: Target, r_t: Target):
        l_sols = self.left_aik.solve(l_t.tform('left_base_link'), tcp2end=Config.left_tcp2end)
        r_sols = self.right_aik.solve(r_t.tform('right_base_link'), tcp2end=Config.right_tcp2end)
        l_sols = [sol for sol in l_sols if self._extra_l_joint_limit(sol)]
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
            return False, None
        prev = (c.sub_config('left_').to_array(), c.sub_config('right_').to_array())

        traj: List[RobotConfig] = []
        dual_path_valid = True
        for idx in range(1, len(l_tfs)):
            _l, max_jump_l = self.left_aik.solve(Target(l_tfs[idx], 'platform').tform('left_base_link'), seed=prev[0],
                                                 tcp2end=Config.left_tcp2end, seed_threshold_deg=12)
            _r, max_jump_r = self.right_aik.solve(Target(r_tfs[idx], 'platform').tform('right_base_link'), seed=prev[1],
                                                  tcp2end=Config.right_tcp2end, seed_threshold_deg=12)
            # rospy.loginfo(f'{idx}: {rad2deg(max_jump_l)} {rad2deg(max_jump_r)}')
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
            self.move_group.set_start_state(start_state)
            print(traj[-1])
            self.move_group.set_joint_value_target(traj[-1].to_dict())
            self.move_group.plan()
            s, p, t, e = self.move_group.plan()
            if s:
                self.move_group.set_start_state(traj[-1].to_robot_states())
                self.move_group.set_joint_value_target(Config.dual_place_config.to_dict())
                s2, p2, t2, e2 = self.move_group.plan()
                if s2:
                    return True, [p, self._configs_to_robot_trajectory(traj[::-1]), self._configs_to_robot_trajectory(traj), p2]
                else:
                    return False, None
            else:
                return False, None
        return False, None

    def _try_single_target(self, tfs: List[Transform], prefix: str, start_state: moveit_msgs.msg.RobotState):
        aik = self.left_aik if 'left' in prefix else self.right_aik
        tcp2end = Config.left_tcp2end if 'left' in prefix else Config.right_tcp2end
        sols = aik.solve(Target(tfs[0], 'platform').tform(f'{prefix:s}base_link'), tcp2end=tcp2end)
        extra_joint_limit = self._extra_l_joint_limit if 'left' in prefix else self._extra_r_joint_limit
        sols = [sol for sol in sols if extra_joint_limit(sol)]
        if not sols:
            rospy.logwarn(f'[_try_single_target] cannot find sols')
            return False, None
        sols.sort(key=lambda _: abs(_[4]))

        other_config = RobotConfig.build_from_robot_state(start_state, 'right_' if 'left' in prefix else 'left_')
        other_config_array = other_config.to_array()

        traj: List[RobotConfig] = []
        print()
        prev = sols[0]
        _path_valid = True
        for idx in range(1, len(tfs)):
            _s, max_jump = aik.solve(Target(tfs[idx], 'platform').tform(f'{prefix:s}base_link'), seed=prev,
                                     tcp2end=tcp2end, seed_threshold_deg=12)
            if not _s:
                rospy.logwarn(f'[_try_single_target] find invalid pt at {idx}')
                _path_valid = False
                break
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
            # mg = self.single_move_group_dict[prefix]
            mg = self.move_group
            mg.set_start_state(start_state)
            mg.set_joint_value_target(traj[-1].to_dict())
            s, p, t, e = mg.plan()
            if s:
                mg.set_start_state(traj[-1].to_robot_states())
                tj = RobotConfig.build_from_robot_state(start_state).update(
                    Config.left_place_config if 'left' in prefix else Config.right_place_config).to_dict()
                mg.set_joint_value_target(tj)
                s2, p2, t2, e2 = self.move_group.plan()
                if s2:
                    return True, [p, self._configs_to_robot_trajectory(traj[::-1]), self._configs_to_robot_trajectory(traj), p2]
                else:
                    return False, None
            else:
                return False, None
        return False, None

    def _gen_paired_targets(self, targets: List[Target], q: Queue):
        targets.sort(key=lambda _t: _t.tform(target_frame='platform').to_point().x, reverse=True)
        targets_num = len(targets)
        start_config = Config.dual_home_config
        waypoint_num = 20
        l_tfs = []
        r_tfs = []
        for t in targets:
            l_tfs.append(self._gen_cartesian_path(t.tform(target_frame='platform').to_point(), num=waypoint_num))
            r_tfs.append(self._gen_cartesian_path(t.tform(target_frame='platform').to_point(), num=waypoint_num))
        for i in range(targets_num):
            for j in range(i + 1, targets_num):
                if targets[j].is_finished:
                    continue
                ret, plans = self._try_dual_targets(l_tfs[i], r_tfs[j], start_config.to_robot_states())
                if ret:
                    targets[i].set_finished()
                    targets[j].set_finished()
                    rospy.loginfo(f'grasp sol found {i} & {j}')
                    q.put(('dual', plans))
                    start_config = Config.dual_place_config
                    break

            if not targets[i].is_finished:
                ret, plans = self._try_single_target(l_tfs[i], 'left_', start_config.to_robot_states())
                if ret:
                    targets[i].set_finished()
                    q.put(('left_', plans))
                    start_config = start_config.update(Config.left_place_config)

        for i in range(targets_num):
            if not targets[i].is_finished:
                ret, plans = self._try_single_target(r_tfs[i], 'right_', start_config.to_robot_states())
                if ret:
                    targets[i].set_finished()
                    q.put(('right_', plans))
                    start_config = start_config.update(Config.right_place_config)
        rospy.loginfo('plan_picking finished.')
        q.put("complete")

    @staticmethod
    def _configs_to_robot_trajectory(configs: List[RobotConfig]) -> moveit_msgs.msg.RobotTrajectory:
        msg = moveit_msgs.msg.RobotTrajectory()
        msg.joint_trajectory.joint_names = configs[0].get_names()
        msg.joint_trajectory.points = []
        for idx, c in enumerate(configs):
            msg.joint_trajectory.points.append(c.to_trajectory_point(idx))
        return msg

    def _exec_pick_place(self, q: Queue):
        while True:
            item = q.get()
            if isinstance(item, str):
                break
            else:
                prefix = item[0]
                plans = item[1]
                ret = self._robot_client.open_hand(prefix)
                rospy.sleep(0.1)
                if not ret:
                    rospy.logwarn("open_hand 失败, 请人工介入")
                    break
                ret = self._robot_client.dual_move(plans[:2], prefix)
                if not ret:
                    rospy.logwarn("pre pick 失败, 请人工介入")
                    break
                rospy.sleep(0.1)
                ret = self._robot_client.close_hand(prefix)
                rospy.sleep(0.1)
                if not ret:
                    rospy.logwarn("close_hand 失败, 请人工介入")
                    break
                ret = self._robot_client.grasp(prefix)
                if not ret:
                    rospy.logwarn("grasp 失败, 请人工介入")
                    break
                ret = self._robot_client.dual_move(plans[2:], prefix)
                if not ret:
                    rospy.logwarn("place 失败, 请人工介入")
                    break
                rospy.sleep(0.1)
                ret = self._robot_client.open_hand(prefix)
                if not ret:
                    rospy.logwarn("open_hand 失败, 请人工介入")
                    break


if __name__ == '__main__':
    rospy.init_node('center')
    server = PickingSystem()
    rospy.loginfo("start center service")
    rospy.spin()
