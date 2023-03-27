#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2021/10/25 下午6:53
"""
import time

import moveit_commander
import pickingv2.srv
import rospy
from base.tools import moveit_error_code_to_string


class JointPlanSrv:
    def __init__(self):
        # self.scene = moveit_commander.PlanningSceneInterface()
        # self.rc = moveit_commander.RobotCommander()
        self.move_group_dict = {}
        self.srv = rospy.Service('JointPlan', pickingv2.srv.JointPlan, self._handle)

    def _get_move_group(self, name) -> moveit_commander.MoveGroupCommander or None:
        if name not in self.move_group_dict:
            try:
                self.move_group_dict[name] = moveit_commander.MoveGroupCommander(name)
            except Exception as e:
                return None
        return self.move_group_dict[name]

    def _handle(self, req: pickingv2.srv.JointPlanRequest) -> pickingv2.srv.JointPlanResponse:
        resp = pickingv2.srv.JointPlanResponse()
        print("recv req")
        time.sleep(3)
        print("complete")
        # move_group: moveit_commander.MoveGroupCommander = self._get_move_group(req.move_group_name)
        # if not move_group:
        #     resp.success = False
        #     resp.desc = f'cannot find a move group named {req.move_group_name}'
        #     return resp
        # state = move_group.get_current_state()
        # state.joint_state.position = list(state.joint_state.position)
        # for i in range(len(state.joint_state.name)):
        #     if req.joint_names[i] == state.joint_state.name[i]:
        #         state.joint_state.position[i] = req.start_joint_config[i]
        # move_group.set_start_state(state)
        # target_dict = {}
        # for i in range(len(req.joint_names)):
        #     target_dict[req.joint_names[i]] = req.target_joint_config[i]
        # s, p, t, e = move_group.plan(target_dict)
        # resp.success = s
        # resp.trajectory = p
        # resp.desc = moveit_error_code_to_string(e)
        return resp


if __name__ == '__main__':
    rospy.init_node("JointPlanSrv")
    jps = JointPlanSrv()
    rospy.spin()
