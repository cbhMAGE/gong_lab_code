#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy, actionlib,pymongo
from sensor_msgs.msg import MultiDOFJointState
from Motion_config import Motion_config

class Mongo_Database(self):
	def __init__(self): 
        
        self.client = pymongo.MongoClient('mongodb://localhost:27017') #声明本地路径数据库
        #库中生成名为iwi的集合
		self.db = self.client.iwi
		self.col_motion = self.db['motion']
		self.new = True
		rospy.init_node("perception_mongo_sender")
		rospy.loginfo("Mongodb sender init") #初始化节点
		sub = rospy.subsriber("Mongo_db", MultiDOFJointState, callback)

	def create_new_motion(self):
		if self.new ==True:
            #

		self.new  = False
	def push_data_to(self,data_address,sec,number,one_pose_data):
		push_data = {}
		push_data['time'] = sec
		push_data['joint_number'] = number
		push_data['motion_data'] = one_pose_data
		self.col_motion.insert('')

	def callback(self,msg_mong_receive):
		create_new_motion()
		sec = msg_mong_receive.header.stamp.to_sec() #float 64
		#sec = msg_mong_receive.header.stamp.secs #int 32
		#nec = msg_mong_receive.header.stamp.necs # int 32
		#jianglaigaichengzidian
		number = len(msg_mong_receive.joint_names)

		one_pose_data = list()
		num = 0
		for jointname in msg_mong_receive.joint_names:
			one_joint_data = list()
			x = msg_mong_receive.twist[num].angular.x
			y = msg_mong_receive.twist[num].angular.y
			z = msg_mong_receive.twist[num].angular.z
			one_joint_data.append(jointname)
			one_joint_data.append(x)
			one_joint_data.append(y)
			one_joint_data.append(z)
			one_pose_data.append(one_joint_data)
			num = num+1
		push_data_to(self.data_address,sec,number,one_pose_data)

if __name__ == "__main__":
	Mongo_Database()
	rate = rospy.Rate(10) # 10hz
	while not rospy.is_shutdown():
		#hello_str = "hello world %s" % rospy.get_time()
		#rospy.loginfo(hello_str)
		rate.sleep()
