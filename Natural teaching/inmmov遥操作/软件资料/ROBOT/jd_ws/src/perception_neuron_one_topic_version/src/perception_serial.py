#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sensor_msgs.msg import JointState
import rospy, serial
from perception_serial_sender import *
from joint import *

if __name__ == "__main__":
	rospy.init_node("perception_serial")
	rospy.loginfo("ROS Serial init") #初始化串口节点

	#port_name = rospy.get_param('~port','/dev/ttyUSB0')
	port_name = rospy.get_param('~port')
	#baud = int(rospy.get_param('~baud','115200'))
	baud = rospy.get_param('~baud')
	#tim=0.1
	tim = rospy.get_param('~timeout')

	try:
		ser = serial.Serial(port_name,baud,timeout=tim) #创建串口句柄。
		rospy.loginfo('open serial successful.')
		rospy.sleep(0.2)

	except Exception, e:
		try:
			#port_name=rospy.get_param('~port','/dev/ttyUSB1')
			port_name=rospy.get_param('~port_try')
			ser=serial.Serial(port_name,baud,timeout=tim)
			rospy.sleep(0.2)
		except Exception,e:
			rospy.loginfo('open serial failed.')
			ser=1
	if ser!=1:
		b=ser.readall()
		rospy.loginfo(b)

	robotjoints = rospy.get_param('~robotjoints')
	joints_instance = list()
	for jointname in robotjoints:
		joints_instance.append(Joint(jointname))
	joints_dict = dict(zip(robotjoints, joints_instance))

	a=perceptionsender(joints_dict,ser)
	rate = rospy.Rate(10) # 10hz
	rospy.loginfo("Started perception_serial")
	while not rospy.is_shutdown():
		#hello_str = "hello world %s" % rospy.get_time()
		#rospy.loginfo(hello_str)
		rate.sleep()
