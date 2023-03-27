#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: Zhiyu YANG
@email: ZhiyuYANG96@outlook.com
@time: 2022/3/16 下午11:29
"""
import time

import rospy
import moveit_msgs.srv
import numpy as np
import sensor_msgs.msg

check_validity_srv = rospy.ServiceProxy('/check_state_validity', moveit_msgs.srv.GetStateValidity)


def check_validity(s) -> bool:
    req = moveit_msgs.srv.GetStateValidityRequest()
    req.group_name = 'arm'
    req.robot_state.joint_state.name = ['joint_' + str(i) for i in range(1, 7)]
    req.robot_state.joint_state.position = s
    resp: moveit_msgs.srv.GetStateValidityResponse = check_validity_srv.call(req)
    # print(resp)
    return resp.valid


data_filename = "/home/msi/CLionProjects/RPT/test/test_collision_check.txt"
data_result_filename = "/home/msi/CLionProjects/RPT/test/test_collision_check_result.txt"


def main():
    with open(data_filename, "r") as f:
        data = f.readlines()

    with open("result.txt", "w") as f:
        total_cost = 0
        for row in data[1:]:
            vals = list(map(float, row.strip().split()))
            t1 = time.time()
            is_valid = check_validity(vals)
            total_cost += time.time() - t1
            f.write(f"{str(not is_valid)} 0.0\n")
        print(f"avg. {1000.0 * total_cost / (len(data) - 1)} ms")


def gen_test_file(idx=None):
    with open(data_filename, "w") as f:
        n = 5000
        np.random.seed(16)
        data = np.random.uniform(-np.pi, np.pi, (n, 6))
        if idx is not None:
            f.write(f"{idx.stop - idx.start}\n")
            data = data[idx]
        else:
            f.write(f"{n:d}\n")

        for i, row in enumerate(data):
            f.write(" ".join(map(str, row)))
            f.write("\n")
            if i == 0:
                publish(row.tolist())
    with open(data_filename, "r") as f:
        data = f.readlines()
    with open(data_result_filename, "w") as f:
        total_cost = 0
        for row in data[1:]:
            vals = list(map(float, row.strip().split()))
            t1 = time.time()
            is_valid = check_validity(vals)
            cur_cost = time.time() - t1
            f.write(f"{str(not is_valid)} {cur_cost * 1000.0:.5f}\n")
            total_cost += cur_cost
        print(f"avg. {1000.0 * total_cost / (len(data) - 1)} ms")


def publish(pos):
    pub = rospy.Publisher("/jaka_joint_states", sensor_msgs.msg.JointState, queue_size=10)
    msg = sensor_msgs.msg.JointState()
    msg.name = ['joint_' + str(i) for i in range(1, 7)]
    msg.position = pos
    msg.header.stamp = rospy.Time.now()
    for _ in range(30):
        pub.publish(msg)
        rospy.sleep(0.1)


def check_result():
    #    cpp_result = "/home/msi/CLionProjects/RPT/cmake-build-debug/result.txt"
    cpp_result = "/home/msi/result.txt"
    # cpp_result = "/home/msi/CLionProjects/RPT/build/result.txt"
    ros_result = "./result.txt"
    with open(cpp_result, "r") as f:
        cpp_data = f.readlines()
    with open(ros_result, "r") as f:
        ros_data = f.readlines()
    for i in range(len(cpp_data)):
        if cpp_data[i].split()[0].lower() != ros_data[i].split()[0].lower():
            print(f"line `{i}` error {cpp_data[i].split()[0].lower():s}")
    print("check complete")


if __name__ == '__main__':
    rospy.init_node("aa", anonymous=True)
    # gen_test_file(idx=slice(0, 1))
    gen_test_file()
    # main()
    # check_result()
    # rospy.spin()
