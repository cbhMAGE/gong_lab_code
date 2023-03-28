#ifndef Link_H
#define Link_H

#include <ros/ros.h>
#include <ros/package.h>
#include <std_msgs/Float32MultiArray.h>

#define pi 3.1415926
#define xyz 1
#define xzy 2
#define yzx 3
#define yxz 4
#define zxy 5
#define zyx 6

typedef double float64;


class Link
{
public:
	Link()
	{
		anglex_=0.0;
		angley_=0.0;
		anglez_=0.0;
		direction_=yxz;
	}

    Link(std::string na,int direct)
    {
    		anglex_=0.0;
		angley_=0.0;
		anglez_=0.0;
		name_=na;
		direction_=direct;

    }
    Link(std::string na)
    {
    	              anglex_=0.0;
		angley_=0.0;
		anglez_=0.0;
		name_=na;
		
    }

	~Link(){};

	void setangle(float eulerX,float eulerY,float eulerZ )
	{
		angley_=eulerY;
		anglex_=eulerX;
		anglez_=eulerZ;
	}


	float64 anglex(){return anglex_;}
	float64 angley(){return angley_;}
	float64 anglez(){return anglez_;}
	int direction(){return direction_;}
	std::string name(){return name_;}
private:

float64 anglex_;
float64 angley_;
float64 anglez_;
int direction_;
std::string name_;

};
#endif	