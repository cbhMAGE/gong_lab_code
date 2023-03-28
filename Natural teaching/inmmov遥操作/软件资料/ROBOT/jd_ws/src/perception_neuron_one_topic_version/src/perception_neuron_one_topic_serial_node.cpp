#include <ros/ros.h>
#include <ros/package.h>
#include <sensor_msgs/JointState.h>
#include <serial/serial.h>

class serialpublisher{

public:
    serialpublisher(ros::NodeHandle & nh):nh_(nh){
        to = serial::Timeout::simpleTimeout(3000);
        baud=115200;
        sleeptime=ros::Duration(3);
        port="/dev/ttyUSB0";



    try
    {
    //set the property of the port and open it.
        ser.setPort(port);
        ser.setBaudrate(baud);
        ser.setTimeout(to);
        ser.open();
    }
    catch (serial::IOException &e)
    {
        ROS_ERROR_STREAM("Unable to open port ");       
        //return -1;
    }
    catch(serial::SerialException &e)
    {
      ROS_ERROR_STREAM("Serial port already open. ");       
    }



    }
    ~serialpublisher(){}

void prepare()
{
    while(!ser.isOpen())
    {
        port="/dev/ttyUSB1";
      try
    {
    //set the property of the port and open it.
        ser.setPort(port);
        ser.setBaudrate(baud);
        ser.setTimeout(to);
        ser.open();
    }
    catch (serial::IOException &e)
    {
        ROS_ERROR_STREAM("Unable to open port ");       
    }
     catch(serial::SerialException &e)
    {
      ROS_ERROR_STREAM("Serial port already open. ");       
    }


    sleeptime.sleep();
    port="/dev/ttyUSB0";
      try
    {
    //set the property of the port and open it.
        ser.setPort(port);
        ser.setBaudrate(baud);
        ser.setTimeout(to);
        ser.open();
    }
    catch (serial::IOException &e)
    {
        ROS_ERROR_STREAM("Unable to open port ");       
    }
     catch(serial::SerialException &e)
    {
      ROS_ERROR_STREAM("Serial port already open. ");       
    }

    }

    sleeptime.sleep();

    ROS_INFO("Connected !");

    sub = nh_.subscribe("/Controller_joint_states", 5, &serialpublisher::callback,this);
    ROS_INFO("End preparation");

}



private:
    serial::Serial ser;
    ros::NodeHandle nh_;
    ros::Duration sleeptime;
    serial::Timeout to;
    uint32_t baud;
    ros::Subscriber sub;
    std::string rl;
    std::string port;
    char *p;

    void callback(const sensor_msgs::JointStateConstPtr & angle_data)
    {
       int len=angle_data->name.size();
       for(int i=0;i<len;i++){
        //data_process()
        ser.write(angle_data->name.at(i));
        rl=ser.readline();
        ROS_INFO("%s",rl.c_str());
       }
       ROS_INFO("Finish writing!");


}


void data_process(){

}

};




int main(int argc, char** argv){

    ROS_INFO("starting");
    ros::init( argc, argv, "perception_neuron_one_topic_serial_node" );
    ros::NodeHandle nh;
    serialpublisher serialpub(nh);
    serialpub.prepare();

    ros::Rate rate(50.0);
    ros::spin();
    return 0;
}


