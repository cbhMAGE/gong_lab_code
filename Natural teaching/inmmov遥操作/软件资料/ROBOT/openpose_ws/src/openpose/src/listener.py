#!/usr/bin/env python
# -*- coding: utf-8 -*-
import rospy,serial
from std_msgs.msg import Int16MultiArray
from Motion_config import Motion_config

pi=3.1415926

class robot_controller:

    def __init__(self):   
        self.fakejoints = ['left_thumb','left_index','left_middle','left_ring','left_pinky','left_hand','left_bicep','left_bicep_rotate',
        'left_shoulder_side','left_shoulder_up','head_leftright','head_updown','right_bicep','right_bicep_rotate','right_shoulder_side',
        'right_shoulder_up','right_thumb','right_index','right_middle','right_ring','right_pinky','right_hand',
        'waist_rotate','waist_lean','waist_front','jaw']
        md = Motion_config('/home/pn/openpose_ws/src/openpose/src/motion_config.txt', self.fakejoints)
        llxd = md.readdata()
        self.fake_min =llxd[0]
        self.fake_max =llxd[1]
        for i in range(len(self.fake_min)):
            self.fake_min[i]=self.fake_min[i]*1.0/180*pi
            self.fake_max[i]=self.fake_max[i]*1.0/180*pi
        self.fakejoints_min=dict(zip(self.fakejoints,self.fake_min))
        self.fakejoints_max=dict(zip(self.fakejoints,self.fake_max))
        rospy.loginfo("ROS Serial init") #
        self.serial_init()
        rospy.loginfo("ROS_config") #
        rospy.init_node('listener', anonymous=True)
        rospy.Subscriber("chatter", Int16MultiArray, self.callback)
        # spin() simply keeps python from exiting until this node is stopped
        rospy.spin()

    def serial_init(self):
        # port_name = rospy.get_param('~port')
        # baud = rospy.get_param('~baud')
        # tim = rospy.get_param('~timeout')
        self.port_name = '/dev/ttyUSB0'
        self.baud = 115200
        self.tim=0.1
        try:
            self.ser = serial.Serial('/dev/ttyUSB0',115200,timeout=0.1)#创建串口句柄。
            self.ser.open()
            rospy.loginfo('open serial successful.')
            rospy.sleep(0.2)
        except Exception, e:
            try:
                #port_name=rospy.get_param('~port','/dev/ttyUSB1')
                # port_name=rospy.get_param('~port_try')
                self.ser=serial.Serial('/dev/ttyUSB1',115200,timeout=0.1)
                self.ser.open()
                rospy.loginfo('open serial successful.')
                rospy.sleep(0.2)
            except Exception,e:
                rospy.loginfo('open serial failed.')
                self.serflag=1
        if self.serflag!=1:
            b=self.ser.readall()
            rospy.loginfo(b)

        # if not self.ser.isOpen():
        #    self.ser.open()
        #    rospy.loginfo('open serial successful.')
        #    rospy.sleep(0.2)
        # b=self.ser.readall()
        # rospy.loginfo(b)  # read mega2560 initializing message and print

    def data_process(self, data):
        joints_num = len(self.fakejoints)
        lis = list()
        lis.append(255)
        lis.append(255)
        control_data = []
        for i in range(joints_num):
            if i == 6:
                control_data.append(data[1])  # inverse
            elif i == 8:
                control_data.append(data[0])
            else:
                control_data.append(0)
        #msgtomongo=UInt8MultiArray()
        #msgtomongo.dim.label = 'raw_joint_data_without_time'
        #msgtomongo.dim.stride = 1
        dic=dict(zip(self.fakejoints, control_data))
        #rospy.logwarn(dic["left_bicep"])
        for i in range(joints_num):
            if dic.has_key(self.fakejoints[i])  and (self.fakejoints_max[self.fakejoints[i]]-self.fakejoints_min[self.fakejoints[i]])!=0:
                #self.lis.append(dic[self.fakejoints[i]])
                #rospy.loginfo(self.fakejoints[i]);
                #rospy.logwarn(dic[self.fakejoints[i]]);
                #tmp=0
                dic[self.fakejoints[i]] = dic[self.fakejoints[i]]*1.0/180*pi
                tmp=dic[self.fakejoints[i]]
                if dic[self.fakejoints[i]]<=self.fakejoints_min[self.fakejoints[i]]:
                    tmp=self.fakejoints_min[self.fakejoints[i]]
                elif dic[self.fakejoints[i]]>=self.fakejoints_max[self.fakejoints[i]]:
                    tmp=self.fakejoints_max[self.fakejoints[i]]
                tmp=(tmp-self.fakejoints_min[self.fakejoints[i]])/(self.fakejoints_max[self.fakejoints[i]]-self.fakejoints_min[self.fakejoints[i]])
                tmp=int(tmp*235)+20
                #rospy.loginfo("%d    %d",i,tmp)
                if i == 6:
                    lis.append(256-tmp)
                    rospy.loginfo(tmp)
                elif i ==8 :
                    lis.append(256-tmp)
                    rospy.loginfo(tmp)
                else:
                    lis.append(0)
                #msgtomongo.data.append(tmp)
            else:
                lis.append(0)
                #msgtomongo.data.append(0)

        #msgtomongo.dim.size = self.lis.size()-2
        #self.pub.publish(msgtomongo)
        length=joints_num+2

        crc16=self.calculateCRC(lis,length)
        lis.append(crc16 >> 8) # checksum
        lis.append(crc16 & 0xFF)
        #rospy.loginfo(self.lis)
        #rospy.loginfo(len(self.lis))
        self.trajectory=lis
        lis=list()
        return self.trajectory

    def calculateCRC(self, data, length):
        temp=0xFFFF
        for i in range(0,length):
            temp=temp ^ data[i]
            for j in range(1,9):
                flag=temp & 0x0001
                temp >>= 1
                if flag:
                    temp ^= 0xA001
        temp2=temp >> 8
        temp=(temp << 8) | temp2
        temp &= 0xFFFF
        return temp


    def data_send(self, data):
            tim=0.1
            judge=0
            #rospy.loginfo(self.serial.isOpen())#确认串口已成功打开。
            joints_num = len(data) #带上编号和时间的数据长
            # print(joints_num)
            #read###################
            for j in range(joints_num):
                try:
                    #if j==16:
                        #rospy.loginfo("%d    %d",j,self.trajectory[j])
                    # if j == 10:
                    #    print(data[j])
                    self.ser.write(chr(data[j]))
                except AttributeError:
                    rospy.logwarn('ser has no attribute related to serial.')
                    break
            b=self.ser.readall()
            rospy.logwarn(b)
            #rospy.sleep(0.09)
            #record
            self.trajectory=list()

    def callback(self, data):
        left_shoulder_side = data.data[0]
        left_bicep = data.data[1]
        # rospy.loginfo("receive_data") #
        data_to_send = self.data_process(data.data)
        # rospy.loginfo("data_process_finish") #
        self.data_send(data_to_send)
        # rospy.loginfo("successful!!!!!!!!!!!!!") #
        # rospy.loginfo(str(left_shoulder_side)+ str(left_bicep))

if __name__ =='__main__':
    robot_controller = robot_controller()





    

    
    


    

    
