#ifndef JOINT_H
#define JOINT_H

#include <ros/ros.h>
#include <ros/package.h>
#include <std_msgs/Float32MultiArray.h>


typedef double float64;

class Joint
{
public:
	Joint()
	{
		position_=0.0;
		velocity_=0.0;
		effort_=0.0;

	}
	Joint(std::string na)
	{
		position_=0.0;
		velocity_=0.0;
		effort_=0.0;
		name_=na;

	}

	Joint(std::string na,int counter, int a){
		position_=0.0;
		velocity_=0.0;
	    effort_=0.0;

		setprepare(na,counter,a);
	}

    ~Joint(){};

    void setprepare(std::string na){
    	name_=na;
    }

    void setprepare(std::string na,int counter, int a){
    	name_=na;
    	counterpart_=counter;
    	direct_=a;
    }
    void setmsg(float64 p,float64 v)
    {
    	position_=p;
    	velocity_=v;
    }

    std::string name(){return name_;}
    int counterpart(){return counterpart_;}
    float64 position(){return position_;}
    float64 oldposition(){return oldposition_;}
    float64 velocity(){return velocity_;}
    float64 effort(){return effort_;}
    int direct(){return direct_;}

private:
    std::string name_;
	int counterpart_;
	float64 position_;
	float64 oldposition_;
	float64 velocity_;
	float64 effort_;
	int direct_;
};


#endif

