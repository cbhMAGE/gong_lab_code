// PerceptionNeuronROSserial.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "ros.h"
#include <Windows.h>
#include <geometry_msgs\Pose.h>
#include <std_msgs\Float32MultiArray.h>
#include <std_msgs\MultiArrayLayout.h>
#include <std_msgs\MultiArrayDimension.h>
#include <std_msgs\Int32MultiArray.h>
#include <std_msgs\String.h>
#include <string>
#include <stdlib.h>
#include <sstream>
#include <stdexcept>
#include <iostream>
#include <fstream>
#include <vector>
#include <typeinfo>
#include "WindowsSocket.h"
#include <stdio.h>
#include "NeuronDataReader.h"
#include <conio.h> 
#include<time.h>
using namespace std;
template <class Type>
Type stringToNum(const string& str)
{
	istringstream iss(str);
	Type num;
	iss >> num;
	return num;
}
SOCKET_REF sockTCPREF = NULL;
FrameDataReceived _DataReceived;
CalculationDataReceived _CmdDataReceived;
BvhDataHeader     _bvhHeader;
SocketStatusChanged    _SocketStatusChanged;


int addi = 3;
float * _valuesBuffer = NULL;
int _frameCount = 0;
int bufferLength = 0;
bool bCallbacks = false;
double rate = 20;
double sleeptime = 1e3 / rate;
int len1, len2;

// Max Array Length for ROS Data = 255  should be for UINT8 (-> data_msg.data_length )
// But not working maybe they used somewhere signed int8
// -> therefore the max array length = 127.

// we split Axis Neuron Data in 3 Parts -> therefore
//int MAX_DATA_LENGTH = 120;

/* com communication*/
char buffer[] = "30.0000";
char test[] = "30.0000";
DWORD btsIO;
float data2[3] = { 0,0,0 };






struct MyCallbacks {

	static void __stdcall bvhDataReceived(void * customObject, SOCKET_REF sockRef, BvhDataHeader* header, float * data)
	{
		
		//end = clock();
		//period = end - start;
		//start = end;
		//printf("data frequency=%f\n", 1e3/ period);
		BvhDataHeader * ptr = header;

		
		if (ptr->DataCount != bufferLength || _valuesBuffer == NULL) {
			_valuesBuffer = new float[ptr->DataCount+addi];
			bufferLength = ptr->DataCount;
		}
		//printf("start=%X\n", ptr->Token1);
		//printf("end=%X\n", ptr->Token2);
		//printf("datacount=%d\n", ptr->DataCount);
		//printf("withdisp=%d\n", ptr->WithDisp);
		//printf("withreference=%d\n", ptr->WithReference);
		//printf("frameindex=%u\n", ptr->FrameIndex);
		//printf("AvatarIndex=%u\n", ptr->AvatarIndex);
		//printf("Avatarname=%u\n", ptr->AvatarIndex);

		

		/*put additional code here*/

		len1 = ptr->DataCount * sizeof(float);
		len2 = ptr->DataCount;
		//printf("len1=%d\n", len1);
		memcpy((char *)_valuesBuffer, (char*)data, len1);
		//printf("len1=%d", len1);

		//printf("%f,%f,%f,%f,%f,%f,%f\n", _valuesBuffer[353], _valuesBuffer[354],_valuesBuffer[355],_valuesBuffer[356],_valuesBuffer[357],_valuesBuffer[358],_valuesBuffer[359]);
		//printf("\n");

	}
	static void __stdcall calculationDataReceived(void* customedObj, SOCKET_REF sockRef, CalcDataHeader* header, float* data) {
		printf("Data received!! \n");
	}

	static void __stdcall socketStatusChanged(void * customObject, SOCKET_REF sockRef, SocketStatus status, char * message) {
		printf("Socket status changed\n");

	}


	virtual void registerNeuronCallbacks() {
		bool bBVH = false;
		bool bCmd = false;
		bool bSSt = false;


		BRRegisterFrameDataCallback(this, bvhDataReceived);

		BRRegisterCalculationDataCallback(this, calculationDataReceived);

		BRRegisterSocketStatusCallback(this, socketStatusChanged);
		

		printf("Register Neuron Callbacks");
	}


};

MyCallbacks cbks;





void prepareDataMsg(std_msgs::Float32MultiArray & data_msg) {
	data_msg.layout.dim = (std_msgs::MultiArrayDimension *) malloc(sizeof(std_msgs::MultiArrayDimension) * 2);
	data_msg.layout.dim[0].label = "PerceptionNeuronData";
	data_msg.layout.dim[0].size = 180+3;
	// adapted ros_lib/ros/node_handle.h buffer limitations to 1024 (max would be 2048)
	// that we can use MAX_DATA_LENGTH for data_msg.data_length.
	data_msg.data_length = 180+3;
	data_msg.layout.data_offset = 0;
	data_msg.data = (float *)malloc(sizeof(float) * 500);
}

int main(int argc, _TCHAR * argv[])
{
	/*com operation*/
	//float p[1];
	//创建串口
	bool error_flag = 0;
	HANDLE hDevice = CreateFile(L"COM5",  //注意COM1~COM10与COM10以上的窗口的命名规则
		GENERIC_READ | GENERIC_WRITE,   //使用读写方式
		0,
		0,
		OPEN_EXISTING,
		0,
		0);
	if (hDevice != INVALID_HANDLE_VALUE)
	{
		printf("Port opened!\n");
		DCB lpTest;
		GetCommState(hDevice, &lpTest);  //获取当前的参数设置
		lpTest.BaudRate = CBR_9600;       //设置波特率
		lpTest.ByteSize = 8;              //数据位数为8
		lpTest.Parity = NOPARITY;         //无校验
		lpTest.StopBits = ONESTOPBIT;   //1位停止位
		SetCommState(hDevice, &lpTest);  //设置通信参数
		
	}
	else
	{
		error_flag = 1;
	}



	// first set some default values if no config file found
	std::string ipAxisNeuron = "192.168.1.5";
	std::string ipROS = "192.168.1.4";
	int portAxisNeuron = 7001;
	bool verbose = true;

	// read config file
	std::ifstream fin("config.txt", std::ios::in);
	std::string line;
	std::istringstream iss;
	if (fin.is_open())
	{
		printf("Reading values from config.txt\n");
		while (fin.good())
		{
			std::getline(fin, line);
			iss.str(line.substr(line.find("=") + 1));
			if (line.find("ipAxisNeuron") != std::string::npos) {
				printf("IP Axis Neuron %s \n", iss.str().c_str());
				iss >> ipAxisNeuron;

			}
			else if (line.find("portAxisNeuron") != std::string::npos) {
				printf("Port Axis Neuron %s \n", iss.str().c_str());
				iss >> portAxisNeuron;
			}
			else if (line.find("ipROS") != std::string::npos) {
				printf("IP ROS Serial Server %s \n", iss.str().c_str());
				iss >> ipROS;
			}
			iss.clear();
		}
		fin.close();
	}
	else
	{
		printf("Unable to open config.txt file.. using DEFAULT values. \n");
		printf("ROS Master (Serial Windwos): 192.168.1.4, Axis Neuron 192.168.1.5. \n");
		printf("The config file will be read if use the commandline \n");
		printf("  cd to PerceptionNeuronROSSerial path, start PerceptionNeuronROSserial.exe .. \n");
	}

	// ROS Handle
	ros::NodeHandle nh;
	char *ros_master = new char[ipROS.length() + 1];
	strcpy(ros_master, ipROS.c_str());

	printf("\nConnecting to ROS Master (ROS Serial Server) at %s \n", ros_master);
	/*test*/
	nh.initNode(ros_master);
	// Neuron Connection
	void * neuronptr = NULL;
	void * cmdptr = NULL;

	if (BRGetSocketStatus(neuronptr) == SocketStatus::CS_Running) {
		BRCloseSocket(neuronptr);
	}


	printf("Okay, we after the if SocketStatus::CS_Running\n");

	char *nIP = new char[ipAxisNeuron.length() + 1];
	strcpy(nIP, ipAxisNeuron.c_str());

	printf("Okay, calluing BRConnectTo IP: %s port %d\n", nIP, portAxisNeuron);


	neuronptr = BRConnectTo(nIP, portAxisNeuron);
	//cmdptr = BRConnectDataPipe(nIP, portAxisNeuron);
	if (neuronptr == NULL) {
		printf("Axis Neuron Connection refused! \n ");
		printf("Trying again... \n");
		//return 0;
	}
	else {
		printf("Connected to Axis Neuron at %s \n", nIP);
	}

	//cmdptr = BRConnectCmdPipe(nIP, 7009);

	/*if (cmdptr == NULL) {
		printf("Cmd Port refused! \n ");
		printf("Trying again... \n");
		//return 0;
	}
	else {
		printf("Connected to Cmd Port at %s \n", nIP);
	}*/

	cbks.registerNeuronCallbacks();

	printf("\n \nAdvertising Axis Neuron Data to ROS Serial Server\n");

	// Prepare the data msg arrays for the ros publisher


	std_msgs::Float32MultiArray data_msg_1;
	prepareDataMsg(data_msg_1);



	ros::Publisher data_pub_1("/perception_neuron/data_1", &data_msg_1);

	nh.advertise(data_pub_1);
	

	while (1)
	{
		if(error_flag ==0)
		{
			ReadFile(hDevice, buffer, strlen(test), &btsIO, NULL);    //读取数据
			std::string s;
			s = buffer;
			double bb = stringToNum<double>(s);
			float a;
			a = (float)bb;
			data2[0] = a;
		}
		{
			data2[0] = 0;
		}
		
		if (verbose) {
			//printf("Current Data Frame %i \n", _frameCount);
		}

		// check that it have already received values from Axis Neuron
		if (_valuesBuffer != NULL) {
			//bool r = BRZeroOutAll(cmdptr);

			//Publish part one of the array

			memcpy((char*)(_valuesBuffer + len2), (char*)data2, 12);

			data_msg_1.data = _valuesBuffer;

			data_pub_1.publish(&data_msg_1);
			printf("%f\n", data_msg_1.data[53]);

				//for (int i =0;i <= 180;i++)
				//printf("i=%d,%f\n", i, data_msg_1.data[i]);
		

		}

		nh.spinOnce();
		Sleep(sleeptime);
	}
	BRCloseSocket(neuronptr);
	printf("All done!\n");
	CloseHandle(hDevice);    //关闭串口 

	return 0;
}