#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/12/21 下午12:48

lianxu caizhai
"""
import numpy as np
import rospy
import moveit_commander
import moveit_msgs.srv
import moveit_msgs.msg
from base.dto import RobotConfig, Point, Transform, Euler, rad2deg, deg2rad, Target
from base.ik import AnalyticalIK
from typing import Union, List
import visualization_msgs.msg
import std_msgs.msg
from copy import deepcopy
import qjaka_gui.srv
import pickingv2.srv
import trajectory_msgs.msg
import threading
import geometry_msgs.msg
from base.config import Config


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
        self.vel_scale = 0.8
        self.acc_scale = 0.6
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
                req.rotate_deg = 60
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
        if prefix == "left_":
            return self.do([0], [False])
        elif prefix == "right_":
            return self.do([1], [False])
        else:
            return self.do([0, 1], [False, False])

    def close_hand(self, prefix):
        if prefix == "left_":
            return self.do([0], [True])
        elif prefix == "right_":
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
        print(len(new_pts))
        # "time_optimal_trajectory_generation"
        # "iterative_spline_parameterization"
        # "iterative_time_parameterization"
        return move_group.retime_trajectory(
            move_group.get_current_state(), msg, velocity_scaling_factor=self.vel_scale,
            acceleration_scaling_factor=self.acc_scale,
            algorithm='iterative_time_parameterization'
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

    def gen_disp_traj(self, trajectories: List[moveit_msgs.msg.RobotTrajectory]):
        trajectory = self._combine_plans(trajectories, self.dual_move_group)
        print(len(trajectory.joint_trajectory.points))
        ret, t = self._sample(trajectory)
        print(len(t.joint_trajectory.points))
        if not ret:
            rospy.logerr("call sample filter failed in RobotClient.dual_move")
            return False
        disp_msg = moveit_msgs.msg.DisplayTrajectory()
        disp_msg.trajectory_start = self.dual_move_group.get_current_state()
        disp_msg.trajectory = [t]
        return disp_msg, self._trajectory_to_list(t)


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

        self.fk = rospy.ServiceProxy("/compute_fk", moveit_msgs.srv.GetPositionFK)

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

    def publish_end_path(self, pts: List, frame_id: str, ):
        ans = [[], []]
        for i in range(0, len(pts[0]), 12):
            req = moveit_msgs.srv.GetPositionFKRequest()
            req.robot_state.joint_state.name = [f'left_joint_{i:d}' for i in range(1, 7)]
            req.robot_state.joint_state.name.extend([f'right_joint_{i:d}' for i in range(1, 7)])
            _pt = deepcopy(pts[0][i:i + 6])
            _pt.extend(pts[1][i + 6:i + 12])
            req.robot_state.joint_state.position = _pt
            req.fk_link_names = ["left_gripper_base_link", "right_gripper_base_link"]
            resp: moveit_msgs.srv.GetPositionFKResponse = self.fk(req)
            # print(resp)
            # exit(0)
            ans[0].append(Transform.build_from_pose_msg(resp.pose_stamped[0]) * Euler.build_from_deg(0, -90, 0).to_tform())
            ans[1].append(Transform.build_from_pose_msg(resp.pose_stamped[1]) * Euler.build_from_deg(0, -90, 0).to_tform())
        self.publish_grasp_path(ans[0], frame_id=frame_id, idx=0)
        self.publish_grasp_path(ans[1], frame_id=frame_id, idx=1)

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


def fk(state: moveit_msgs.msg.RobotState, prefix: str):
    fk_srv = rospy.ServiceProxy("/compute_fk", moveit_msgs.srv.GetPositionFK)
    req = moveit_msgs.srv.GetPositionFKRequest()
    req.robot_state = state
    req.fk_link_names = [f"{prefix}link_6"]
    resp: moveit_msgs.srv.GetPositionFKResponse = fk_srv(req)
    return Transform.build_from_pose_msg(resp.pose_stamped[0])


def configs_to_robot_trajectory(configs: List[RobotConfig]) -> moveit_msgs.msg.RobotTrajectory:
    msg = moveit_msgs.msg.RobotTrajectory()
    msg.joint_trajectory.joint_names = configs[0].get_names()
    msg.joint_trajectory.points = []
    for idx, c in enumerate(configs):
        msg.joint_trajectory.points.append(c.to_trajectory_point(idx))
    return msg


class Tool:
    def __init__(self):
        self.left_aik = AnalyticalIK(prefix="left_", robot_type='zu7_v1')
        self.right_aik = AnalyticalIK(prefix="right_", robot_type='zu7_v2')

    def gen_cartesian_traj(self, target_config: List, prefix: str, num=50) -> List[RobotConfig]:
        target_tf = fk(RobotConfig.build_from_jvals(deg2rad(target_config), prefix=prefix).to_robot_states(), prefix=prefix)
        msg = moveit_msgs.msg.RobotTrajectory()
        msg.joint_trajectory.joint_names = [f"{prefix}joint_{i}" for i in range(1, 7)]
        aik = self.left_aik if 'left' in prefix else self.right_aik
        prev = deg2rad(target_config)
        ans = [RobotConfig.build_from_jvals(prev, prefix)]
        for i in np.linspace(0, 0.2, num=num):
            mid_tf = target_tf * Transform.build_from_euler_point(Euler(), Point(0, 0, -i))
            sol, _ = aik.solve(Target(mid_tf, frame_id="platform").tform(f"{prefix}base_link"), seed=prev, seed_threshold_deg=15)
            if len(sol) == 0:
                print(_, i)
                rospy.logerr("c failed")
                exit(-1)
            prev = sol[0]
            ans.append(RobotConfig.build_from_jvals(sol[0], prefix))
        return ans


def main():
    # 00
    # targets = [
    #     ([-100.2, 65.7, -78.4, 190.6, 84.1, 33.1, ], [103.5, 128.6, 75.4, -3.7, -147.5, 8.2, ]),
    #     ([-121.9, 57.2, -71.3, 190.6, 142.6, -15.1, ], [66.5, 131.7, 63.0, 121.6, 39.6, 39.5, ]),
    #     (None, [64.0, 137.6, 46.3, 11.5, -40.4, -24.0, ]),
    # ]
    # 11
    targets = [
        ([-100.2, 65.7, -78.4, 190.6, 84.1, 33.1, ], [83.1, 116.3, 41.5, 47.5, -88.7, -20.2]),
        ([-121.9, 57.2, -71.3, 190.6, 142.6, -15.1, ], [96.2, 110.9, 82.3, -6.3, -115.5, 50.5]),
        (None, [71.0, 128.4, 60.5, 3.7, -58.5, -135.9, ]),
    ]

    dual = moveit_commander.MoveGroupCommander("dual_arm")
    # left = moveit_commander.MoveGroupCommander("left_arm")
    # right = moveit_commander.MoveGroupCommander("right_arm")
    dual.set_planner_id("BKPIECE")
    dual.set_planning_time(10)
    pub = rospy.Publisher("yzy_path", moveit_msgs.msg.DisplayTrajectory, queue_size=1)

    # print(left.get_end_effector_link())
    # print(right.get_end_effector_link())
    tool = Tool()
    rc = RobotClient(dual)
    rt = RvizTool()

    c_num = 30
    #
    # cur_config = deepcopy(Config.dual_home_config)
    all_tasks = []
    prev_state = dual.get_current_state()
    for i in range(len(targets)):
        l, r = targets[i]
        cur_config = deepcopy(Config.dual_home_config)
        pre_config = deepcopy(cur_config)
        c_configs = [
            deepcopy(cur_config) for j in range(c_num)
        ]
        place_config = deepcopy(cur_config)
        if l is not None:
            l_configs = tool.gen_cartesian_traj(l, "left_", c_num)
            for j in range(c_num):
                c_configs[j] = c_configs[j].update(l_configs[j])
            pre_config = pre_config.update(l_configs[-1])
            place_config = place_config.update(Config.left_place_config)

        if r is not None:
            r_configs = tool.gen_cartesian_traj(r, "right_", c_num)
            for j in range(c_num):
                c_configs[j] = c_configs[j].update(r_configs[j])
            pre_config = pre_config.update(r_configs[-1])
            place_config = place_config.update(Config.right_place_config)

        dual.set_start_state(prev_state)
        dual.set_joint_value_target(Config.dual_home_config.to_dict())
        s0, p0, t0, e0 = dual.plan()
        if not s0:
            rospy.logerr("000 failed")
            return

        dual.set_start_state(Config.dual_home_config.to_robot_states())
        dual.set_joint_value_target(pre_config.to_dict())
        s1, p1, t1, e1 = dual.plan()
        if not s1:
            rospy.logerr("111 failed")
            return

        dual.set_start_state(pre_config.to_robot_states())
        dual.set_joint_value_target(place_config.to_dict())
        s2, p2, t2, e2 = dual.plan()
        if not s2:
            rospy.logerr("222 failed")
            return
        _prefix = "dual"
        if l is None:
            _prefix = "right_"
        if r is None:
            _prefix = "left_"
        all_tasks.append([
            [p0], [_prefix, p1, configs_to_robot_trajectory(c_configs[::-1])],
            [configs_to_robot_trajectory(c_configs), p2]
        ])
        prev_state = deepcopy(place_config.to_robot_states())
        # plans = [
        #     # p0,
        #     p1,
        #     configs_to_robot_trajectory(c_configs[::-1]),
        #     # configs_to_robot_trajectory(c_configs),
        #     # p2,
        # ]
        # disp_msg, traj_msg = rc.gen_disp_traj(plans)
        # r = rospy.Rate(1)
        # while not rospy.is_shutdown():
        #     # rt.publish_end_path(traj_msg, frame_id="platform")
        #     pub.publish(disp_msg)
        #     r.sleep()

    for _task in all_tasks:
        rc.dual_move(_task[0])
        rospy.sleep(1)
        _prefix = _task[1][0]
        rc.open_hand(_prefix)
        rc.dual_move(_task[1][1:], _prefix)
        rc.close_hand(_prefix)
        # rc.grasp(_prefix)
        rc.dual_move(_task[2], _prefix)
        rc.open_hand(_prefix)
    print("main end")


if __name__ == '__main__':
    rospy.init_node("p_plan_t2", anonymous=True)
    main()
