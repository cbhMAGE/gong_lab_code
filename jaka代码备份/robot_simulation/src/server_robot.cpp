/**
 * 此代码为机械臂关节角的接收代码
 * 基于websocket，Ubuntu作为服务器，Windows端为客户端
 * 先启动服务器程序，再启动客户端程序
 */

#include <unistd.h>
#include <stdio.h>
#include <x86_64-linux-gnu/sys/socket.h>
#include <netinet/in.h>
#include <x86_64-linux-gnu/sys/types.h>
#include <stdlib.h>
#include <string.h>

#include <ros/ros.h>
#include <geometry_msgs/Twist.h>
#include <sensor_msgs/JointState.h>
#include <iostream>
#include <vector>

using namespace std;

#define SERVER_PORT 4000 //端口号
#define LENGTH_OF_LISTEN_QUEUE 20
#define BUFFER_SIZE 1000

int main(int argc, char* argv[])
{

    ros::init(argc, argv, "joint_state_publisher");

    // 创建节点句柄
    ros::NodeHandle m_nh;

    // 创建一个Publisher，发布名为/joint_states的topic，消息类型为sensor_msgs::JointState，队列长度5
    ros::Publisher m_jointStatePub = m_nh.advertise<sensor_msgs::JointState>("joint_states", 5);

    // 设置循环的频率，这里需要和发送频率进行匹配
    ros::Rate loop_rate(200);



    struct sockaddr_in server_addr;
    int server_socket;
    int opt = 1;

    bzero(&server_addr, sizeof(server_addr)); // 置字节字符串前n个字节为0，包括'\0'
    server_addr.sin_family = AF_INET;
    server_addr.sin_addr.s_addr = htons(INADDR_ANY); // 转小端,INADDR_ANY就是指定地址为0.0.0.0的地址
    server_addr.sin_port = htons(SERVER_PORT);

    // 创建一个Socket
    server_socket = socket(PF_INET, SOCK_STREAM, 0);

    if (server_socket < 0)
    {
        printf("Create Socket Failed!\n");
        exit(1);
    }


    // bind a socket
    setsockopt(server_socket, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));
    if (bind(server_socket, (struct sockaddr*)&server_addr, sizeof(server_addr)))
    {
        printf("Server Bind Port: %d Failed!\n", SERVER_PORT);
        exit(1);
    }

    // 监听Socket
    if (listen(server_socket, LENGTH_OF_LISTEN_QUEUE))
    {
        printf("Server Listen Failed!\n");
        exit(1);
    }

    while (1)
    {

        struct sockaddr_in client_addr;
        int client_socket;
        socklen_t length;
        char Buffer[BUFFER_SIZE];

        // 连接客户端Socket
        length = sizeof(client_addr);
        client_socket = accept(server_socket, (struct sockaddr*)&client_addr, &length);
        if (client_socket < 0)
        {
            printf("Server Accept Failed!\n");
            break;
        }

        // 从客户端接收数据
        while (1)
        {
            //bzero(Buffer, BUFFER_SIZE);
            //length = recv(client_socket, Buffer, BUFFER_SIZE, 0);

            //aaa
            double recvMsg[12];
            memset(recvMsg,0,sizeof(recvMsg));
            char *pRecvMsg = (char*)&recvMsg[0];
            for (int i=0;i<12;i++)
            {
                recv(client_socket,pRecvMsg,sizeof(double)*12,0);
                //printf("ok");
                printf("%lf\n", recvMsg[i]);
                pRecvMsg++;
            }
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

            m_jointStateMsg.position[0] = -recvMsg[0]-1.5;
            m_jointStateMsg.position[1] = -recvMsg[1];
            m_jointStateMsg.position[2] = recvMsg[2]+1.57;
            m_jointStateMsg.position[3] = recvMsg[3];
            m_jointStateMsg.position[4] = recvMsg[4]+3.14;
            m_jointStateMsg.position[5] = recvMsg[5];
            m_jointStateMsg.position[6] = recvMsg[6]-2.5;
            m_jointStateMsg.position[7] = -recvMsg[7];
            m_jointStateMsg.position[8] = recvMsg[8]+1.57;
            m_jointStateMsg.position[9] = recvMsg[9]+3.14;
            m_jointStateMsg.position[10] = recvMsg[10];
            m_jointStateMsg.position[11] = recvMsg[11];


            // 发布消息
            m_jointStatePub.publish(m_jointStateMsg);


            // 按照循环频率延时
            loop_rate.sleep();

        }
    }

    close(server_socket);
    return 0;
}
