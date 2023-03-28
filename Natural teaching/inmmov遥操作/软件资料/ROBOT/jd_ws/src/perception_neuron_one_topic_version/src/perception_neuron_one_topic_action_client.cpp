#include <ros/ros.h>
#include <ros/package.h>
#include <sensor_msgs/JointState.h>
void callback(const sensor_msgs::JointStateConstPtr & angle_data, serial::Serial &ser)
{
	len=angle_data->name.size();
	for(int i=0;i<len;i++)
	{
		
	}

}

int main(int argc, char** argv){

    ROS_INFO("starting");
    ros::init( argc, argv, "perception_neuron_one_topic_action_client" );
    ros::NodeHandle nh;

    serial::Serial ser;
    try
    {
    //set the property of the port and open it.
        ser.setPort("/dev/ttyUSB0");
        ser.setBaudrate(115200);
        serial::Timeout to = serial::Timeout::simpleTimeout(3000);
        ser.setTimeout(to);
        ser.open();
    }
    catch (serial::IOException&amp; e)
    {
        ROS_ERROR_STREAM("Unable to open port ");
        return -1;
    }

    ros::Subscriber sub = nh.subscribe("/Controller_joint_states", 5, &callback,this,ser);

    ros::Rate rate(50.0);
    ros::spin();
    return 0;
}


