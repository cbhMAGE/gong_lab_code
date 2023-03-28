#!/usr/bin/env python
# -*- coding: utf-8 -*-
class Motion_config:
	def __init__(self,filename,jointslist):
		self.__filename = filename
		self.__jointslist = jointslist
	def __pre_treatment(self,filename):
		__using_string = list()
		for line in open(filename,'r'):
			#replace tab with space
			line = line.expandtabs()
			#clear space
			line = line.replace(' ','')
			if line != "\n" :
			#	print "//",
			#else: 
				line = line.replace('\n','')
				#ignore comments
				if line[0] != '#' :
					#print"****"
				#else:
					#print line,
					__using_string.append(line)
		return __using_string
	def search_information(self,jointname):
		jointname = jointname.replace('\n','')
		head_flag = 0
		end_flag = 0
		lenth = len(self.__predata)
		rawdata = list()
		rawdata.append(jointname)
		for i in range (lenth):
			if (self.__predata[i]).find(jointname+':') == -1:
				#print '',
				head_flag = 0
			elif i == lenth and head_flag == -1:
				#cannot find this joint's head,please check config flie
				break
			else:
				head_flag = 1
				for j in range (i+1, lenth):
					if (self.__predata[j]).find(jointname+';') == -1:
						rawdata.append(self.__predata[j])
					elif j == lenth and end_flag == -1:
						#cannot find this joint's end,please check config flie
						print 'end word error:'+jointname
					else:
						end_flag = 1
						#print rawdata
						return rawdata
				break
		if head_flag == 0:
			print 'head word error:'+jointname
			return -1 #head word error
		if end_flag == 0:
			print 'end word error:'+jointname
			return -2 #end word error
	def make_datalist(self,joint_rawdata):
		min_list= list()
		max_list= list()
		for i in range (len(joint_rawdata)):
			for j in range(1,len(joint_rawdata[i])):
				if (joint_rawdata[i][j]).find('min=') != -1:
					joint_rawdata[i][j]=joint_rawdata[i][j].replace('min=','')
					min_list.append(float(joint_rawdata[i][j]))
				elif j == len(joint_rawdata):
					print "error min :"+ joint_rawdata[i][0]
				if (joint_rawdata[i][j]).find('max=') != -1:
					joint_rawdata[i][j]=joint_rawdata[i][j].replace('max=','')
					max_list.append(float(joint_rawdata[i][j]))
				elif j == len(joint_rawdata):
					print "error max :"+ joint_rawdata[i][0]
		return min_list,max_list
	def readdata(self):
		#get data after pre_treatment
		self.__predata = self.__pre_treatment(self.__filename)
		#divide data according to the jointnames
		return self.make_datalist(map(self.search_information,self.__jointslist))
