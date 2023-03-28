#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial, time

def send():
	name="file.txt"
	file =open(name,'r')
	for line in file:
		tmp=line.replace('\n','').split(',')
		for i in range(0,28):
			temp=int(tmp[i])
			#print(temp)
			ser.write(chr(temp))
			#print(temp)
		#b=ser.readall()
		#print('\n')
		b=ser.readline()
		print(b)
		time.sleep(0.2)
	file.close()

if __name__ == "__main__":

	#port_name = rospy.get_param('~port','/dev/ttyUSB0')
	port_name = '/dev/ttyUSB0'
	baud =115200
	tim = 0
	ser = serial.Serial(port_name,baud,timeout=tim) #创建串口句柄。
	print('open serial successful.')
	time.sleep(0.2)
	b=ser.readline()
	print(b)
	b=ser.write('s')
	b=ser.readline()
	print(b)
	print("send")
	while 1:
		send()

