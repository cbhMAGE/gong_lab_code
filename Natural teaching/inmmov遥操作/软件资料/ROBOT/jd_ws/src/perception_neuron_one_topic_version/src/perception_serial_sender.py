#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy, actionlib, serial
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt8MultiArray
from Motion_config import Motion_config


pi=3.1415926

class perceptionsender:
	def __init__(self,joints_dict,ser):
		self.serial=ser
		self.joints_dict = joints_dict
		self.joints = rospy.get_param('~elmo_driver/joints') 
		self.fakejoints=rospy.get_param('~fakejoints')
		self.count = 0
		#md = Motion_config('/home/pn/catkin_ws/src/perception_neuron_one_topic_version/src/motion_config.txt',self.fakejoints)
		md = Motion_config('/home/pn/jd_ws/src/perception_neuron_one_topic_version/src/motion_config.txt',self.fakejoints)
		llxd = md.readdata()

		self.fake_min=llxd[0]
		self.fake_max=llxd[1]

		for i in range(len(self.fake_min)):
			self.fake_min[i]=self.fake_min[i]*1.0/180*pi
			self.fake_max[i]=self.fake_max[i]*1.0/180*pi
		self.fakejoints_min=dict(zip(self.fakejoints,self.fake_min))
		self.fakejoints_max=dict(zip(self.fakejoints,self.fake_max))

		self.sub=rospy.Subscriber("Controller_joint_states",JointState,self.callback)

		#self.pub=rospy.Publisher('datatomongo',UInt8MultiArray,1000)
		#self.sub=rospy.Subscriber("Controller_joint_states_check",JointState,self.callback)
		rospy.loginfo("starting subscription" )

	def callback(self,data):
		#for i in range(len(data.name)):
		#rospy.loginfo(data.name[i])
		self.data_process(data)
		self.data_send()

	
	def data_process(self,data):
		joints_num = len(self.fakejoints)
		#a=int(data.header.stamp.secs*1.0*1e3 + data.header.stamp.nsecs*1.0/1e6)
		#h_a=a>>8 
		#l_a=a&0x00FF
		self.lis = list()
		self.lis.append(255) #动作编号
		self.lis.append(255)
		#self.lis.append(h_a)
		#self.lis.append(l_a) #该时间点距离开始时刻的时间间隔

		#msgtomongo=UInt8MultiArray()
		#msgtomongo.dim.label = 'raw_joint_data_without_time'
		#msgtomongo.dim.stride = 1

		dic=dict(zip(data.name,data.position))
		#rospy.logwarn(dic["left_bicep"])
		self.dic=dic;
		for i in range(joints_num):
			if dic.has_key(self.fakejoints[i])  and (self.fakejoints_max[self.fakejoints[i]]-self.fakejoints_min[self.fakejoints[i]])!=0:
				#self.lis.append(dic[self.fakejoints[i]])
				#rospy.loginfo(self.fakejoints[i]);
				#rospy.logwarn(dic[self.fakejoints[i]]);

				#tmp=0
				tmp=dic[self.fakejoints[i]]
				if dic[self.fakejoints[i]]<=self.fakejoints_min[self.fakejoints[i]]:
					tmp=self.fakejoints_min[self.fakejoints[i]]
				elif dic[self.fakejoints[i]]>=self.fakejoints_max[self.fakejoints[i]]:
					tmp=self.fakejoints_max[self.fakejoints[i]]
				tmp=(tmp-self.fakejoints_min[self.fakejoints[i]])/(self.fakejoints_max[self.fakejoints[i]]-self.fakejoints_min[self.fakejoints[i]])
				tmp=int(tmp*254)+1
				#rospy.loginfo("%d    %d",i,tmp)
				self.lis.append(tmp)
				#msgtomongo.data.append(tmp)
			else:
				self.lis.append(0)
				#msgtomongo.data.append(0)
		
		#msgtomongo.dim.size = self.lis.size()-2
		#self.pub.publish(msgtomongo)
		length=joints_num+2

		crc16=self.calculateCRC(length)
		self.lis.append(crc16 >> 8) # checksum
		self.lis.append(crc16 & 0xFF)
		#rospy.loginfo(self.lis)
		#rospy.loginfo(len(self.lis))
		self.trajectory=self.lis
		self.lis=list()

	def calculateCRC(self,length):
		temp=0xFFFF
		for i in range(0,length):
			temp=temp ^ self.lis[i]
			for j in range(1,9):
				flag=temp & 0x0001
				temp >>= 1
				if flag:
					temp ^= 0xA001
		temp2=temp >> 8
		temp=(temp << 8) | temp2
		temp &= 0xFFFF
		return temp

	def data_send(self):
		

		tim=0.1
		self.judge=0
		#rospy.loginfo(self.serial.isOpen())#确认串口已成功打开。
		joints_num = len(self.trajectory) #带上编号和时间的数据长
		if type(self.serial)==type(1):
			try:
				port_name = rospy.get_param('~port')
				baud = int(rospy.get_param('~baud'))
				tim=rospy.get_param('timeout')
				self.serial = serial.Serial(port_name,baud,timeout=tim) #创建串口句柄。
   # rospy.loginfo('open serial successful.')
			except Exception, e:
				try:
					port_name=rospy.get_param('~port_try')
					self.serial=serial.Serial(port_name,baud,timeout=tim)
				except Exception,e:
					rospy.loginfo('open serial failed.')
					self.serial=1

		#read###################
		self.read = False 
		File_name_read = "/home/pn/jd_ws/src/perception_neuron_one_topic_version/src/motion_record_10.txt"
		File_name_record = '/home/pn/jd_ws/src/perception_neuron_one_topic_version/src/motion_record_10.txt'
		if self.read == True:	
			name=File_name_read
			file =open(name,'r')
			lines=file.readlines()
			len_file=len(lines)
			line=lines[self.count]
			tmp=line.replace('\n','').split(',')
			for i in range(0,30):
				self.trajectory[i]	=int(tmp[i]);	
			file.close()
			if self.count<len_file-1:
				self.count=self.count+1

		for j in range(joints_num):
			try:
				#if j==16:
					#rospy.loginfo("%d    %d",j,self.trajectory[j])
				self.serial.write(chr(self.trajectory[j]))
			except AttributeError:
				rospy.logwarn('ser has no attribute related to serial.')
				break
		#b=self.serial.readall()
		#rospy.logwarn(b)
		#rospy.sleep(0.09)


		#record
		if self.read ==  False:
			if self.count==0:
				f=open(File_name_record,'w')
				self.count=1
			else:
				f=open(File_name_record,'a')

			for i in range(joints_num):
				f.write(str(self.trajectory[i])+",")	
			f.write('\n')
			f.close()
		self.trajectory=list()


		


