

import rospy
import numpy as np
from base.dto import Euler, Point, Target, Transform
from base.ik import AnalyticalIK
import moveit_msgs.srv

rospy.init_node("shunxu", anonymous=True)

phi = (1+np.sqrt(5))/2.0
directions12 = [
    [1, 1, 1],
    [-1, -1, -1],
    [-1, 1, 1],
    [1, -1, 1],
    [1, 1, -1],
    [1, -1, -1],
    [-1, 1, -1],
    [-1, -1, 1],
    [0, phi, 1/phi],
    [0, -phi, 1/phi],
    [0, phi, -1/phi],
    [0, -phi, -1/phi],
    [1/phi, 0, phi],
    [-1/phi, 0, phi],
    [1/phi, 0, -phi],
    [-1/phi, 0, -phi],
    [phi, 1/phi, 0],
    [-phi, 1/phi, 0],
    [phi, -1/phi, 0],
    [-phi, -1/phi, 0],
]

directions20 = [
    [0, 1, phi],
    [0, -1, phi],
    [0, 1, -phi],
    [0, -1, -phi],
    [phi, 0, 1],
    [-phi, 0, 1],
    [phi, 0, -1],
    [-phi, 0, -1],
    [1, phi, 0],
    [-1, phi, 0],
    [1, -phi, 0],
    [-1, -phi, 0],
]

aik = AnalyticalIK(prefix="right_", robot_type="zu7_v2")
state_valid_srv = rospy.ServiceProxy(
    '/check_state_validity', moveit_msgs.srv.GetStateValidity)
state_valid_srv.wait_for_service()
state_valid_req = moveit_msgs.srv.GetStateValidityRequest()
state_valid_req.robot_state.joint_state.name = [
    f"right_joint_{i:d}" for i in range(1, 7)]
state_valid_req.group_name = 'right_arm'


def calc_w(t: Target):
    cnt = 0
    directions = directions20
    for dir in directions:
        tf = Transform.build_from_euler_point(Euler(0, np.arccos(
            dir[2]/np.linalg.norm(dir[:2])), np.arctan2(dir[1], dir[0])), t.tform('platform').to_point())
        _t = Target(tf, frame_id="platform")
        sols = aik.solve(_t)
        valid = False
        for sol in sols:
            state_valid_req.robot_state.joint_state.position = sol
            resp: moveit_msgs.srv.GetStateValidityResponse = state_valid_srv(
                state_valid_req)
            if resp.valid:
                valid = True
                print(sol)
        if valid:
            cnt += 1
    return cnt / len(directions)


ts = [
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.132, -0.328, 0.43)), frame_id="platform"),
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.431, -0.234, 0.57)), frame_id="platform"),
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.051, -0.299, 0.53)), frame_id="platform"),
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.616, -0.284, 0.43)), frame_id="platform"),
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.611, -0.321, 0.61)), frame_id="platform"),
    Target(Transform.build_from_euler_point(
        Euler(), Point(0.522, -0.273, 0.63)), frame_id="platform")
]

weights = []
for tt in ts:
    weights.append(calc_w(tt))

print(weights)

N = len(ts)

w_dis = {}
d1 = 0.05
k = 0.5
d2 = 0.3
for i in range(N-1):
    for j in range(i+1, N)
    dis = (ts[i].tform('platform').to_point() -
           ts[j].tform('platform').to_point()).length()
    w_dis[(i, j)] = max(weights[i] + weights[j]) + \
        max(np.exp(-dis/d1), k*(dis-d2))

w_dis = sorted(w_dis, key=lambda _: w_dis[_])
for key in w_dis:
    print(key, w_dis[key])
