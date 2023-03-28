/* perception_neuron_tf_broadcaster.cpp
 *
 * Copyright (C) 2015 Alexander Rietzler, Simon Haller
 * All rights reserved.
 *
 * This software may be modified and distributed under the terms
 * of the BSD license.  See the LICENSE file for details.
 */

#include <ros/ros.h>
#include <ros/package.h>
#include <std_msgs/Float32MultiArray.h>
#include <sensor_msgs/JointState.h>
#include <math.h>
#include <iterator>
#include <sensor_msgs/MultiDOFJointState.h>
#include<geometry_msgs/Twist.h>
#include<geometry_msgs/Vector3.h>

#include "Joint.h"
#include "Link.h"

/*
#define pi 3.1415926
#define xyz 1
#define xzy 2
#define yzx 3
#define yxz 4
#define zxy 5
#define zyx 6
*/

class NeuronBroadcaster
{
public:
    NeuronBroadcaster(ros::NodeHandle & nh)
        :nh_(nh)
    {     
         nh.getParam("link_children_names",link_children_names_);
         nh.getParam("link_parents_names",link_parents_names_);
         nh.getParam("inmoov_joints_names",inmoov_joints_names_);
         nh.getParam("inmoov_moveable_joints_names",inmoov_moveable_joints_names_);
         nh.getParam("link_useful_names",link_useful_names_);
         nh.getParam("inmoov_moveable_joints_counterpart",inmoov_moveable_joints_counterpart);
         nh.getParam("inmoov_moveable_joints_direct",inmoov_moveable_joints_direct);
         nh.getParam("link_useful_direction",link_useful_direction);
     }

     ~NeuronBroadcaster(){};


private:
    // all variables
     ros::NodeHandle nh_;
     ros::Subscriber sub;
     ros::Publisher pub;
     ros::Publisher pub_mong;//for mongo_db

     std::vector<std::string> link_children_names_, link_parents_names_,inmoov_joints_names_,
     inmoov_moveable_joints_names_,link_useful_names_;
     std::vector<Joint> joint_instance;
     std::vector<Link> link_instance;
     std::vector<int> inmoov_moveable_joints_direct,joint_index,link_useful_direction,link_index,inmoov_moveable_joints_counterpart;

     //std::string* link_children_names_temp, link_parents_names_temp, inmoov_joints_names_temp, inmoov_moveable_joints_names_temp, link_useful_names_temp;

     int num_all_inmoov_joints,num_inmoov_moveable_joints,num_links,num_useful_links;

     ros::Time oldtime;
     ros::Duration deltatime;


 public:


    void prepare()
    {
    	
        // the following is the preparation of topic format.
        ROS_INFO("preparing");
    	num_all_inmoov_joints=inmoov_joints_names_.size();

    	num_inmoov_moveable_joints=inmoov_moveable_joints_names_.size();

    	num_links=link_children_names_.size();

    	num_useful_links=link_useful_names_.size();

    	int j=0;

    	for(int i=0;i<num_all_inmoov_joints;i++)
    	{
    		if(contain(inmoov_joints_names_.at(i),inmoov_moveable_joints_names_))
    		{

    	    Joint temp(inmoov_moveable_joints_names_.at(j),inmoov_moveable_joints_counterpart.at(j),inmoov_moveable_joints_direct.at(j));
    	    joint_instance.push_back(temp);
    	    joint_index.push_back(i);

    	    j++;

    	    }
    	    else
    	    {

              Joint temp(inmoov_joints_names_.at(i));
              joint_instance.push_back(temp);

    	}
    }
     j=0;
 

    for(int i=0;i<num_links;i++)
    {

    	if(contain(link_children_names_.at(i),link_useful_names_))
    	{
    		Link temp(link_useful_names_.at(j),link_useful_direction.at(j));
    		link_instance.push_back(temp);
    		link_index.push_back(i);
    		j++;
    	}
    	else
    	{
    		Link temp(link_children_names_.at(i));
    		link_instance.push_back(temp);
    	}
    }

            oldtime=ros::Time::now();
// The following part is for actionlib client which is used in the CB function of subscriber.
          //  client.waitForServer();
         //   ROS_INFO("connected to an action server");
            //perception_neuron_one_topic_talk_node::anglegoalGoal goal;

            pub = nh_.advertise<sensor_msgs::JointState>("Controller_joint_states", 5);
            
            pub_mong=nh_.advertise<sensor_msgs::MultiDOFJointState>("Mongo_db",1);

            sub = nh_.subscribe("/perception_neuron/data_1", 5, &NeuronBroadcaster::callback_i,this);

            ROS_INFO("End preparing");
           // for(int i = 0 ;i<num_all_inmoov_joints;i++)
          //  {
          //      ROS_INFO("%s",joint_instance.at(i).name().c_str());
          //  }

    }

    

private:

    bool contain(std::string a,  std::vector<std::string> b)
    {
    	bool sign=false;
    	for(int i=0;i<b.size();i++)
    	{
    		if (a==b.at(i))
    		{
    			sign=true;
    			break;
    		}
    	}
    	return sign;
    }

    void callback_i(const std_msgs::Float32MultiArrayConstPtr & bone_data){

        uint startIdx=0;
        uint link_index=0;
        sensor_msgs::JointState msg;
        sensor_msgs::MultiDOFJointState msg_mong;

        msg.header.stamp=ros::Time::now();
        msg_mong.header.stamp=ros::Time::now();

        deltatime=msg.header.stamp-oldtime;
        double delta;
        delta=deltatime.toSec();
        //ROS_INFO("CODE1");
        for(uint j=0; j <bone_data->data.size()/3-1; j++){
            //ROS_INFO("CODE1_1");

            startIdx=j*3;
            float eulerY,eulerX,eulerZ;
            // modified
            eulerZ=bone_data->data[startIdx+3]/180*pi;
            eulerY=bone_data->data[startIdx+4]/180*pi;
            eulerX=bone_data->data[startIdx+5]/180*pi;
             //ROS_INFO("CODE1_2");
           //ROS_INFO("%d\n",j);
            link_instance.at(j).setangle(eulerX,eulerY,eulerZ);
            //for mongo_db
            msg_mong.joint_names.push_back(link_instance.at(j).name());
            geometry_msgs::Twist twist;
            geometry_msgs::Vector3 vector3;
            vector3.x=eulerX	;
            vector3.y=eulerY;
            vector3.z=eulerZ;
            twist.angular=vector3;
            msg_mong.twist.push_back(twist);

            if (j==59)
            {
                        ROS_INFO("%f",eulerZ);
                        ROS_INFO("%f",eulerY);
                        ROS_INFO("%f",eulerX);

            }
        }
        //ROS_INFO("CODE2");


          pub_mong.publish(msg_mong);





         for(int i=0;i<num_inmoov_moveable_joints;i++)
         {
         	float64 old_position,velocity,position,a,b,c,d;

         	old_position=joint_instance.at(joint_index.at(i)).position();
         	         		             
         	if(joint_instance.at(joint_index.at(i)).direct()==0)
         	{


         		position=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglex();
         		velocity=(position-old_position)/delta;
         		 joint_instance.at(joint_index.at(i)).setmsg(position,velocity);

           
          }
            else if(joint_instance.at(joint_index.at(i)).direct()==1)
         	{

         		position=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).angley();

                 //ROS_INFO("%f",position);
                //ROS_INFO("%s",link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).name().c_str());
         		velocity=(position-old_position)/delta;
         		 joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
                 //ROS_INFO("%s",joint_instance.at(joint_index.at(i)).name().c_str());
           
          }
            else if(joint_instance.at(joint_index.at(i)).direct()==2)
         	{
              // ROS_INFO("%s",joint_instance.at(joint_index.at(i)).name().c_str());
         		position=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglez();
               // ROS_INFO("%f",position);
         		velocity=(position-old_position)/delta;
         		 joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
                // ROS_INFO("%d,%f",joint_index.at(i), joint_instance.at(joint_index.at(i)).position());
           
          }
            else if(joint_instance.at(joint_index.at(i)).direct()==3){

                a = link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglez();
                b = link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).angley();
                c = link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglex();
                position=-acos(cos(a)*cos(b));
                //ROS_INFO("%f", position);
                velocity=(position-old_position)/delta;
                joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
         }

    else if(joint_instance.at(joint_index.at(i)).direct()==4){
    	ROS_INFO("CODE1\n");
    	d=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglex();

                a = link_instance.at(15).anglez();
                b = link_instance.at(15).angley();
                c = link_instance.at(15).anglex();
                 a=cos(a);
                c=cos(c);
                /*
                if(a>0.6)
                    a=0.6;
                else if(a<-0.6)
                    a=-0.6;
                if(c>0.6)
                    c=0.6;
                else if(c<-0.6)
                    c=-0.6;

                b=acos(a*c);
                position=-b+d;
                */
             //  position=-acos(cos(b)*sin(a))+d;
               // ROS_INFO("%f", cos(c));

                position=-acos(cos(b)*cos(a));

                velocity=(position-old_position)/delta;
                joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
         }

         else if(joint_instance.at(joint_index.at(i)).direct()==5){

        d=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglex();

                a = link_instance.at(38).anglez();
                b = link_instance.at(38).angley();
                c = link_instance.at(38).anglex();
                position=-acos(cos(b)*sin(a))+d;
                //ROS_INFO("%f", position);
                velocity=(position-old_position)/delta;
                joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
         }

       else if(joint_instance.at(joint_index.at(i)).direct()==10){

        d=link_instance.at(joint_instance.at(joint_index.at(i)).counterpart()).anglex();

                a = link_instance.at(38).anglez();
                b = link_instance.at(38).angley();
                c = link_instance.at(38).anglex();
                position=-acos(cos(b)*sin(a))+d;
                //ROS_INFO("%f", position);
                velocity=(position-old_position)/delta;
                joint_instance.at(joint_index.at(i)).setmsg(position,velocity);
         }



         if(joint_instance.at(joint_index.at(i)).name()=="left_index"){
            position=link_instance.at(45).anglez()+link_instance.at(44).anglez();
                velocity=(position-old_position)/delta;
                 joint_instance.at(joint_index.at(i)).setmsg(position,velocity);

             }

        else if(joint_instance.at(joint_index.at(i)).name()=="right_index"){

             position=link_instance.at(21).anglez()+link_instance.at(22).anglez();
              velocity=(position-old_position)/delta;
                 joint_instance.at(joint_index.at(i)).setmsg(position,velocity);

        }

           if(joint_instance.at(joint_index.at(i)).name()=="right_hand"){
             position=link_instance.at(15).anglex();
             int num= joint_instance.at(joint_index.at(i)).direct();
             ROS_INFO("hand=%f\n",position);
             ROS_INFO("num=%d\n", num);
         }

}


            oldtime=msg.header.stamp;

          for(int i=0;i<num_all_inmoov_joints;i++)
          {
          	msg.name.push_back(inmoov_joints_names_.at(i));
          	msg.position.push_back(joint_instance.at(i).position());
          	msg.velocity.push_back(joint_instance.at(i).velocity());
          	//if(joint_instance.at(i).name()=="left_pinky")
          	//ROS_INFO("i=%d, position=%f",i,joint_instance.at(i).position());
          }

          pub.publish(msg);
}
};

int main(int argc, char** argv){

    ROS_INFO("starting");
    ros::init( argc, argv, "perception_neuron_one_topic_talk_node" );
    ros::NodeHandle nh;
    NeuronBroadcaster neuronBroadcaster(nh);
    neuronBroadcaster.prepare();

    ros::Rate rate(50.0);
    ros::spin();

    ROS_INFO_STREAM("Bye!");
    return 0;
}
