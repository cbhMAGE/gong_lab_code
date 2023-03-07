#include <unistd.h>
#include <stdio.h>
#include <x86_64-linux-gnu/sys/socket.h>
#include <netinet/in.h>
#include <x86_64-linux-gnu/sys/types.h>
#include <stdlib.h>
#include <string.h>
#include <ros/ros.h>
#include <geometry_msgs/Twist.h>

#define SERVER_PORT 5000
#define LENGTH_OF_LISTEN_QUEUE 20
#define BUFFER_SIZE 1000
using namespace std;
int main(int argc, char* argv[])
{

    // ROS节点初始化
    ros::init(argc, argv, "velocity_publisher");

    // 创建节点句柄
    ros::NodeHandle n;

    // 创建一个Publisher，发布名为/turtle1/cmd_vel的topic，消息类型为geometry_msgs::Twist，队列长度10
    ros::Publisher turtle_vel_pub = n.advertise<geometry_msgs::Twist>("/cmd_vel", 10);

    // 设置循环的频率
    ros::Rate loop_rate(100);

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
            bzero(Buffer, BUFFER_SIZE);
            length = recv(client_socket, Buffer, BUFFER_SIZE, 0);


            if (length < 0)
            {
                printf("Server Recieve Data Failed!\n");
                break;
            }

            if ('q' == Buffer[0])
            {
                printf("Quit!\n");
                break;
            }

            printf("%s\n", Buffer);


            // 初始化geometry_msgs::Twist类型的消息
            geometry_msgs::Twist vel_msg;
            switch(Buffer[0]){
                case 'w':
                    //w
                    vel_msg.linear.x = 1;
                    // 发布消息
                    turtle_vel_pub.publish(vel_msg);
                    sleep(1);
                    vel_msg.linear.x = 0;
                    vel_msg.linear.y = 0;
                    vel_msg.linear.z = 0;
                    vel_msg.angular.x = 0;
                    vel_msg.angular.y = 0;
                    vel_msg.angular.z = 0;
                    turtle_vel_pub.publish(vel_msg);
                    break;
                case 'a':
                    //a
                    vel_msg.angular.z = 1;
                    // 发布消息
                    turtle_vel_pub.publish(vel_msg);
                    sleep(2);
                    vel_msg.linear.x = 0;
                    vel_msg.linear.y = 0;
                    vel_msg.linear.z = 0;
                    vel_msg.angular.x = 0;
                    vel_msg.angular.y = 0;
                    vel_msg.angular.z = 0;
                    turtle_vel_pub.publish(vel_msg);
                    break;
                case 's':
                    //s
                    vel_msg.linear.x = -1;
                    // 发布消息
                    turtle_vel_pub.publish(vel_msg);
                    sleep(1);
                    vel_msg.linear.x = 0;
                    vel_msg.linear.y = 0;
                    vel_msg.linear.z = 0;
                    vel_msg.angular.x = 0;
                    vel_msg.angular.y = 0;
                    vel_msg.angular.z = 0;
                    turtle_vel_pub.publish(vel_msg);
                    break;
                case 'd':
                    //d
                    vel_msg.angular.z = -1;
                    // 发布消息
                    turtle_vel_pub.publish(vel_msg);
                    sleep(2);
                    vel_msg.linear.x = 0;
                    vel_msg.linear.y = 0;
                    vel_msg.linear.z = 0;
                    vel_msg.angular.x = 0;
                    vel_msg.angular.y = 0;
                    vel_msg.angular.z = 0;
                    turtle_vel_pub.publish(vel_msg);
                    break;
                default:
                    printf("错误");
                    vel_msg.linear.x = 0;
                    vel_msg.linear.y = 0;
                    vel_msg.linear.z = 0;
                    vel_msg.angular.x = 0;
                    vel_msg.angular.y = 0;
                    vel_msg.angular.z = 0;
                    turtle_vel_pub.publish(vel_msg);
                    break;
            }


            // 按照循环频率延时
            loop_rate.sleep();
            break;

        }

        close(client_socket);
    }

    close(server_socket);
    return 0;
}