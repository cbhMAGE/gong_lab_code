#!/usr/bin/env python
# license removed for brevity
import rospy
import socket
import time
import json
from std_msgs.msg import Int16MultiArray

class openpose_client:
    
    def client_init(self):
        self.tcp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.tcp_client_socket.connect( ('219.228.121.4', 6666) )
        self.tcp_client_socket.connect( ('192.168.31.100', 6666) )
        print('connect to the server')

    def get_json_data(self):
        self.tcp_client_socket.send('connecting'.encode("utf-8"))
        receive_data_json = self.tcp_client_socket.recv(10240)

        receive_data_dict = json.loads(receive_data_json)
        
        shoulder_leftright_data = receive_data_dict['shoulder_leftright'].encode('raw_unicode_escape')
        elbow_data = receive_data_dict['elbow'].encode('raw_unicode_escape')

        if shoulder_leftright_data[0] == '-':
            #shoulder_leftright_data.replace('-','')
            shoulder_leftright_data = int(float(shoulder_leftright_data))
            # shoulder_leftright_data = -1*shoulder_leftright_data
        else:
            shoulder_leftright_data = int(float(shoulder_leftright_data))
        if elbow_data[0] == '-':
            # elbow_data.replace('-','')
            elbow_data = int(float(elbow_data))
            # elbow_data = -1*elbow_data
        else:
            elbow_data = int(float(elbow_data))
        return_data = list()
        return_data.append(shoulder_leftright_data)
        return_data.append(elbow_data)
        return return_data 

    def json_data_progress(self, data):
        if data[0]<=20:
            data[0] = 20
        elif data[0]>=90:
            data[0] = 90
        else:
            pass
        data[0] = 90 - data[0]
        data[0] = -1*data[0]
        rospy.loginfo(data[0])
        if data[1]<=0:
            data[1] = -1*data[1]
        data[1] = 180-data[1]
        if data[1]>=80:
            data[1] = 80
        data[1] = -data[1]
        return data

def talker():
    robot_client = openpose_client()
    robot_client.client_init()
    pub = rospy.Publisher('chatter', Int16MultiArray, queue_size=10)
    rospy.init_node('talker', anonymous=True)
    rate = rospy.Rate(10) # 10hz
    while not rospy.is_shutdown():
        control_msg = Int16MultiArray()
        cotrol_msg_data_temp = robot_client.get_json_data()
        rospy.loginfo(cotrol_msg_data_temp)
        cotrol_msg_data = robot_client.json_data_progress(cotrol_msg_data_temp)
        control_msg.data.append(cotrol_msg_data[0])
        control_msg.data.append(cotrol_msg_data[1])
        # hello_str = "hello world %s" % rospy.get_time()
        rospy.loginfo(control_msg)
        pub.publish(control_msg)
        rate.sleep()

if __name__ == '__main__':
    try:
        talker()
    except rospy.ROSInterruptException:
        pass