#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/5/2 下午3:11
"""
import rospy
import numpy as np
import sensor_msgs.msg
import moveit_commander
import moveit_msgs.msg
import trajectory_msgs.msg
from planner.stp import State
# import sys
# from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton
#
#
# class MainWindow(QMainWindow):
#     def __init__(self, parent=None, *args, **kwargs):
#         super().__init__(parent, *args, **kwargs)
#         b = QPushButton()
#         b.setText("")
#
#
# if __name__ == '__main__':
#     rospy.init_node("robot_controller")
#     app = QApplication(sys.argv)
#     w = MainWindow(None)
#     w.show()
#     sys.exit(app.exec_())


rospy.init_node("robot_controller")

pub = rospy.Publisher("custom_joint_states", sensor_msgs.msg.JointState, queue_size=1, latch=True)
msg = sensor_msgs.msg.JointState()
# # msg.position = np.deg2rad([70, -60, 30])
# msg.position = np.deg2rad([0, 0, 30])
# msg.name = [f"joint_{i}" for i in range(1, 4)]

mg = moveit_commander.MoveGroupCommander('arm')
vals = mg.get_current_joint_values()
print(vals)
print(np.rad2deg(vals))
# goal = {}
# goal_vals = np.deg2rad([45, 60, -64, 20, -30, 0])
# for i in range(6):
#     goal[f"right_joint_{i + 1}"] = goal_vals[i]
# mg.set_joint_value_target(goal)

states = [
    State(*np.deg2rad([-30, 60, -45, -17, -115, 0])),
    State(*np.deg2rad([45, 60, -64, 20, -30, 0]))
]
msg.position = states[0].data_view.tolist()
# msg.position = np.deg2rad([45, 60, -64, 20, -30, 0])

msg.name = [f"right_joint_{i}" for i in range(1, 7)]

pub.publish(msg)
rospy.sleep(0.2)

trajectory_pub = rospy.Publisher('move_group/display_planned_path', moveit_msgs.msg.DisplayTrajectory, queue_size=1, latch=True)
msg = moveit_msgs.msg.DisplayTrajectory()
msg.model_id = "jaka_single"
traj_msg = moveit_msgs.msg.RobotTrajectory()
traj_msg.joint_trajectory.joint_names = [f"right_joint_{i}" for i in range(1, 7)]
for idx, s in enumerate(states):
    pt = trajectory_msgs.msg.JointTrajectoryPoint()
    pt.positions = s.data_view.tolist()
    pt.time_from_start = rospy.Time.from_sec(idx)
    traj_msg.joint_trajectory.points.append(pt)
msg.trajectory.append(traj_msg)
msg.trajectory_start.joint_state.name = [f"right_joint_{i}" for i in range(1, 7)]
msg.trajectory_start.joint_state.position = states[0].data_view.tolist()
rospy.sleep(0.2)

trajectory_pub.publish(msg)
rospy.sleep(0.2)
