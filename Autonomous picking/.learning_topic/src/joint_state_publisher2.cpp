#define _CRT_SECURE_NO_DEPRECATE 
#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <sensor_msgs/JointState.h>
#include <fstream>
#include <string>
#include <iostream>
#include <vector>
using namespace std;

// 功能：将filename 中的数据（共cols列）读取到_vector中，_vector可视为二维数组
int read_scanf(const string& filename, const int& cols, vector<double*>& _vector)
{
	FILE* fp = fopen(filename.c_str(), "r");
	bool flag = true;
	int i = 0;
	if (!fp)
	{
		cout << "File open error!\n";
		return 0;
	}

	while (flag)
	{
		double* rowArray = new double[cols]; //new一个double类型的动态数组

		for (i = 0; i < cols; i++) //读取数据，存在_vector[cols]中
		{
			if (EOF == fscanf(fp, "%lf", &rowArray[i]))
			{
				flag = false;
				break;
			}
			//输出rowArray存入的数据
			//cout << rowArray[0] << " " << rowArray[1] << " " << rowArray[2] << " " << rowArray[3] << endl;
		}
		if (cols == i) //将txt文本文件中的一行数据存入rowArray中，并将rowArray存入vector中
			_vector.push_back(rowArray);
	}
	fclose(fp);
	return 1;
}


int main(int argc, char **argv)
{
	string file = "/home/msi/1008_catkin_ws/src/learning_topic/src/shuju.txt";
	//txt文件中有12列
	int columns = 12;
	vector<double*> output_vector;
	if (!read_scanf(file, columns, output_vector))
	{
		return 0;
	}

	//output_vector可视为二维数组;输出数组元素：
	int rows = output_vector.size();

	// ROS节点初始化
	ros::init(argc, argv, "joint_state_publisher");

	// 创建节点句柄
	ros::NodeHandle m_nh;

	// 创建一个Publisher，发布名为/joint_states的topic，消息类型为sensor_msgs::JointState，队列长度5
	ros::Publisher m_jointStatePub = m_nh.advertise<sensor_msgs::JointState>("joint_states", 5);

	// 设置循环的频率
	ros::Rate loop_rate(1000);

	while (ros::ok())
	{
		for (int i = 0; i < rows; i++)
		{
			cout<<i<<endl;
				// 初始化sensor_msgs::JointState类型的消息
				sensor_msgs::JointState m_jointStateMsg;

				m_jointStateMsg.name.resize(12);
				m_jointStateMsg.position.resize(12);
				
				m_jointStateMsg.header.stamp = ros::Time::now();
				m_jointStateMsg.name[0] = "left_joint_1";
				m_jointStateMsg.name[1] = "left_joint_2";
				m_jointStateMsg.name[2] = "left_joint_3";
				m_jointStateMsg.name[3] = "left_joint_4";
				m_jointStateMsg.name[4] = "left_joint_5";
				m_jointStateMsg.name[5] = "left_joint_6";
				m_jointStateMsg.name[6] = "right_joint_1";
				m_jointStateMsg.name[7] = "right_joint_2";
				m_jointStateMsg.name[8] = "right_joint_3";
				m_jointStateMsg.name[9] = "right_joint_4";
				m_jointStateMsg.name[10] = "right_joint_5";
				m_jointStateMsg.name[11] = "right_joint_6";

				m_jointStateMsg.position[0] = output_vector[i][0]+1.57;
				m_jointStateMsg.position[1] = output_vector[i][1]-1.57;
				m_jointStateMsg.position[2] = output_vector[i][2]+1.57;
				m_jointStateMsg.position[3] = output_vector[i][3];
				m_jointStateMsg.position[4] = output_vector[i][4];
				m_jointStateMsg.position[5] = output_vector[i][5];
//				m_jointStateMsg.position[6] = output_vector[i][6];
//				m_jointStateMsg.position[7] = output_vector[i][7];
//				m_jointStateMsg.position[8] = output_vector[i][8];
//				m_jointStateMsg.position[9] = output_vector[i][9];
//				m_jointStateMsg.position[10] = output_vector[i][10];
//				m_jointStateMsg.position[11] = output_vector[i][11];
//                m_jointStateMsg.position[0] = 0;
//                m_jointStateMsg.position[1] = 0;
//                m_jointStateMsg.position[2] = 0;
//                m_jointStateMsg.position[3] = 0;
//                m_jointStateMsg.position[4] = 0;
//                m_jointStateMsg.position[5] = 0;
                m_jointStateMsg.position[6] = 0;
                m_jointStateMsg.position[7] = 0;
                m_jointStateMsg.position[8] = 0;
                m_jointStateMsg.position[9] = 0;
                m_jointStateMsg.position[10] = 0;
                m_jointStateMsg.position[11] = 0;
//				m_jointStateMsg.position[6] = output_vector[i][0];
//				m_jointStateMsg.position[7] = output_vector[i][1]+3.14;
//				m_jointStateMsg.position[8] = output_vector[i][2];
//				m_jointStateMsg.position[9] = output_vector[i][3];
//				m_jointStateMsg.position[10] = output_vector[i][4];
//				m_jointStateMsg.position[11] = output_vector[i][5];


				// 发布消息
				m_jointStatePub.publish(m_jointStateMsg);

				
				// 按照循环频率延时
				loop_rate.sleep();
			
			
		}
		
		
	}

	return 0;
}
