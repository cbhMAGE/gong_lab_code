#include <ros/ros.h>
#include <ros/package.h>
#include <sensor_msgs/JointState.h>
#include <math.h>
#include <Eigen/Dense>
#include <map>
#include <vector>
#include <string>
#include <std_msgs/Float64.h>

using namespace Eigen;

class checkcollision
{
	ros::NodeHandle nh_;
        	ros::Subscriber sub;
     	ros::Publisher pub;
             Matrix <int ,9,9>collision_matrix;
             sensor_msgs::JointState msg, oldmsg;
             std::map<std::string,int> index_joint;
             std::vector<int> index_check;
             std::vector<double> check_position;
             std::vector<Vector3d> cord,lre;//cordinate for each joint
             int size=9;
             double leng[5]={40,-30,30,-35,35};//has directions
             double r[4]={5,5,10,10}; //1=2,3=4 using radius
             double b[5]={35,10,10,15,15};//1=2,3=4; actually use b/2
              Vector3d p1,p2;
            // std::vector<std_msgs::Float64>  position;
             //std::vector<std_msgs::Float64> velocity;
             std::vector<std::string> inmoov_moveable_joints_names_, inmoov_joints_names_,inmoov_check_joints;

public:
        checkcollision(ros::NodeHandle &nh);
        ~checkcollision(){};
        void prepare();
private:
     void callback_i( const sensor_msgs::JointState & states);
      void callback_i2( const sensor_msgs::JointState & states);

        Matrix<double,3,3> rot_matrix(float a1,float a2, float a3);
        Matrix<double,3,3> rot_matrix(float a4,int index);
        bool check_collision( std::vector <double> check_p);
        /*----conversion from cell or sphere to cord or r or b----*/
        int s_cord(int i) {  return i-2; }//sphere ranks 5-8
        int c_cord(int i) {return i;}
        int s_r(int i){ return i-5;}
        int c_b(int i){return i;}

        bool cal_collision();
        double norm(Vector3d a) {return a.norm();}
        bool forbidden_area();
        double fsc(Vector3d s1, Vector3d c1, Vector3d c2);
        bool cell_cell_collision(Vector3d c11,Vector3d c12, Vector3d c21, Vector3d c22, double b1,double b2);
        double fcc(Vector3d a,Vector3d b, Vector3d c, Vector3d d);//a-Q1 b-Q3 c-Q2 d-Q4
        bool sphere_cell_collision(Vector3d s1,Vector3d c1,Vector3d c2,double r1, double b2);
        bool sphere_collision(Vector3d s1,Vector3d s2, double r1,double r2);
        void cal_cord();
};

checkcollision::checkcollision(ros::NodeHandle &nh): nh_(nh) 
  {
          ROS_WARN("init");
                collision_matrix<< 0,1,1,6,6,6,6,6,6,
                                                 1,0,2,1,5,1,4,2,4,
                                                 1,2,0,5,1,4,1,4,2,
                                                 6,1,5,0,5,1,4,1,4,
                                                 0,5,1,5,0,4,1,4,1,
                                                 0 ,1,4,1,4,0,3,2,3,
                                                 0,4,1,4,1,3,0,3,2,
                                                 0,2,4,1,4,2,3,0,3,
                                                 0,4,2,4,1,3,2,3,0;

                p1<<-leng[0]/2,0,10;
                p2<<leng[0]/2,0, 10;

                inmoov_moveable_joints_names_=std::vector<std::string>{"head_updown","head_leftright","right_shoulder_up","right_bicep_rotate","right_bicep",
        "right_shoulder_side","right_thumb","right_index","right_middle","right_ring","right_pinky","right_hand",
        "left_shoulder_up","left_bicep_rotate","left_bicep",
        "left_shoulder_side","left_thumb","left_index","left_middle","left_ring","left_pinky","left_hand"};

             inmoov_joints_names_=std::vector<std::string>{"virtual_joint", "base_to_pedestal","pedestal_to_mid_stomach","waist_rotate,disk",
        "waist_lean","chestplate","kinect","head_updown","head_leftright","jaw","skull","left_ear","right_ear",
        "eyes_updown","right_camera","right_eye","right_iris","eye_leftright","left_camera","left_eye","left_iris",
        "left_eye_leftright","face","right_shoulder_up","right_bicep_rotate","right_bicep","right_bicepcover",
        "right_shoulder_side","right_thumb1","right_thumb","right_thumb3","right_index1","right_index","right_index3",
        "right_middle1","right_middle","right_middle3","right_ring1","right_ring","right_ring3","right_ring4","right_pinky1",
        "right_pinky","right_pinky3","right_pinky4","right_handcover","right_cover_handring","right_cover_handpinky","right_cover_thumb",
        "right_cover_index","right_cover_middle","right_cover_ring","right_cover_pinky","right_hand","left_shoulder_up","left_bicep_rotate",
        "left_bicep","left_bicepcover","left_shoulder_side","left_thumb1","left_thumb","left_thumb3","left_index1","left_index","left_index3",
        "left_middle1","left_middle","left_middle3","left_ring1","left_ring","left_ring3","left_ring4","left_pinky1","left_pinky","left_pinky3",
        "left_pinky4","left_handcover","left_cover_handring","left_cover_handpinky","left_cover_thumb","left_cover_index","left_cover_middle",
        "left_cover_ring","left_cover_pinky","left_hand"};

            inmoov_check_joints=std::vector<std::string>{ "right_bicep_rotate","right_shoulder_up" ,"right_shoulder_side", "right_bicep",
        "left_bicep_rotate" ,"left_shoulder_up","left_shoulder_side","left_bicep" };

}

    void checkcollision:: prepare()
	{  
		oldmsg.name=inmoov_joints_names_;

	  for(int i=0;i<inmoov_joints_names_.size();i++){
		index_joint.insert(  std::pair<std::string,int>( inmoov_joints_names_.at(i),i));
		oldmsg.position.push_back(0);
		oldmsg.velocity.push_back(0);

	}
                        for(int i=0;i<inmoov_check_joints.size();i++){
		index_check.push_back(index_joint.at(inmoov_check_joints.at(i))); //the index of check_joints in all joints
	}

	lre.clear();
	for (int i=0;i<5;i++)
	{
		Vector3d ma(leng[i],0,0);
		lre.push_back(ma);
	}



                pub = nh_.advertise<sensor_msgs::JointState>("/Controller_joint_states_check", 5);
                sub = nh_.subscribe("/Controller_joint_states", 5, &checkcollision::callback_i2,this);
            ROS_WARN("prepare finished");
	}
  void checkcollision::callback_i( const sensor_msgs::JointState & states)
         {
            ROS_WARN("123");
         }

void checkcollision::callback_i2(const  sensor_msgs::JointState & states)
         {
           // ROS_WARN("callback");
            check_position.clear();
            int a=index_check.size();
            for(int i=0;i<a;i++)
            {
               //check_position.push_back(0);
                double angle= states.position[index_check.at(i)];
                check_position.push_back(angle);
            }
            


            if (check_collision(check_position)) //no collision
            {
                ROS_WARN("check_ok");
                msg=states;         
                oldmsg=msg;
                pub.publish(msg);
            }
            else 
            {
                    ROS_WARN("check_not_ok");

                      oldmsg.header.stamp=ros::Time::now();
                      pub.publish(oldmsg);
            }

         }


         Matrix<double,3,3> checkcollision:: rot_matrix(float a1,float a2, float a3)
         {
               Matrix<double,3,3>  rot_3,rot_z,rot_y,rot_x;
               rot_z=rot_matrix(a3,3);
               rot_y=rot_matrix(a2,2);
               rot_x=rot_matrix(a1,1);
               rot_3=rot_z*rot_y*rot_x;
         	return rot_3;
         }

            Matrix<double,3,3> checkcollision::rot_matrix(float a4,int index)
         {
         	Matrix<double,3,3> rot_3;
         	if (index==3)
         	{
         		rot_3<<cos(a4),-sin(a4),0,
         		           sin(a4), cos(a4),0,
         		           0          ,0          ,1;

         	}
         	else if(index==2)
         	{
         		rot_3<<cos(a4),0,sin(a4),
         		           0  ,       1, 0 , 
         		            -sin(a4), 0 , cos(a4);
         	}
         	else if (index==1)
         	{
         		rot_3<<1,0,0,
         		           0,cos(a4),-sin(a4),
         		           0 ,sin(a4), cos(a4);
         	}
         	return rot_3;
         }



         bool checkcollision::check_collision( std::vector <double> check_p)
        {
          //  ROS_WARN("start check collision");
        	bool flag=0;
        	cal_cord();//calculate the absolute coordinates of each joint;
           // ROS_WARN("calculate cordinate");
        	flag=cal_collision();
        	return flag;
        }
        bool checkcollision:: cal_collision()
        {
        	int flag=1;//0 for collision 1 for ok
        	for(int i=1;i<size;i++)
        	{
        		for(int j=0;j<i;j++)
        		{
        		            int sel=collision_matrix(i,j);
                                  //  ROS_WARN("i=%d,j=%d",i,j);
                                    
        		            switch(sel)
        		            {
        		            	case 1:
        		            		break;
        		            	case 2:
        		            		break;
        		            	case 3:
                                                           //ROS_WARN("case3");

        		            		flag=sphere_collision(cord.at(s_cord(i)),cord.at(s_cord(j)),r[s_r(i)],r[s_r(j)]);
        		            		break;
        		              case 4:
                                                          // ROS_WARN("case 4");
        		               	//flag=sphere_cell_collision(cord.at(s_cord(i)()),cord.at(j),cord.at(j+2),r(i-1),);
        		                           flag=sphere_cell_collision(cord.at(s_cord(i)),cord.at(c_cord(j)),cord.at(c_cord(j)+2),
        		                           	r[s_r(i)],b[c_b(j)]);
        		               	break;
        		              case 5:
                                                            //ROS_WARN("case 5");
        		                          	flag=cell_cell_collision(cord.at(c_cord(i)),cord.at(c_cord(i)+2),
        		                          		cord.at(c_cord(j)),cord.at(c_cord(j)+2),
        		                          		b[c_b(i)],b[c_b(j)]);
        		                          	break;
        		              case 6:
                                                //ROS_WARN("case 6");
        		              	flag=forbidden_area();
        		              	break;
        		               }

        		               if(flag==0){
        		               	return 0;
        		            }
        		}
            }
        		return 1;
        	}

    
        bool checkcollision::forbidden_area()
        {
        	bool flag=1;//1 for ok, 0 for collision
        	double d[4];
        	Vector3d temp;
        	for(int i=1;i<5;i++)
        	{
                //ROS_WARN("i=%d",i);
        		temp=cord.at(i+2);
               // ROS_WARN("cord");
        		d[i-1]=sqrt(pow(temp(0),2)+pow(temp(2),2));
             //   ROS_WARN("judge");
        		if (d[i-1]<(0.5*b[i]+0.5*b[0]))
        		{
        			flag=0;//if one of them cannot ,then break and collision for whole
        			break;
        		}
        	}
        	return flag;
        }
        double checkcollision::fsc(Vector3d s1, Vector3d c1, Vector3d c2)
        {
        	Vector3d c1s1,c1c2,c2s1,c2c1;
        	c1s1=c1-s1;
        	c1c2=c1-c2;
        	c2s1=c2-s1;
        	c2c1=c2-c1;
        	double d;
        	if( c1s1.dot(c1c2) >=0 && c2s1.dot(c2c1)>=0)
        	{
        		d=c1s1.dot(c1c2);
        		d=d/norm(c1c2);
        		d=pow(d,2);
        		d=sqrt(pow(norm(c1s1),2)-d);
        	}
        	else if(c2s1.dot(c2c1)<0)
        	{
        		d=norm(c2s1);
        	}
        	else if(c1s1.dot(c1c2)<0)
        	{
        		d=norm(c1s1);
        	}
        	return d;
        }

        bool checkcollision::cell_cell_collision(Vector3d c11,Vector3d c12, Vector3d c21, Vector3d c22, double b1,double b2)
        {
        	Vector3d c11c12=c11-c12;
        	Vector3d c21c22=c21-c22;
        	double c;
        	c=norm(c11c12.cross(c21c22));
        	double d;
        	if(c==0)
        	{
        		d=std::min(fsc(c11,c21,c22),fsc(c12,c21,c22));
        		d=std::min(d,fsc(c21,c11,c12));
        		d=std::min(d,fsc(c22,c11,c12));
        	}
        	else
        	{
        		d=fcc(c11,c12,c21,c22);
        	}
        	int flag=0;
        	if(d>=0.5*(b1+b2))
        	{
        		flag=1;
        	}
        	return flag;
        }

        double checkcollision::fcc(Vector3d a,Vector3d b, Vector3d c, Vector3d d)
        {//a-Q1 b-Q3 c-Q2 d-Q4
        	double f1ab,f1cd,f2,f3ab,f3cd;
        	double distance;
        	f1ab=norm(a-b)*norm(a-b);
        	f1cd=norm(c-d)*norm(c-d);
        	f2=(b-a).dot(d-c);
        	f3ab=(b-a).dot(c-a);
        	f3cd=(d-c).dot(c-a);
        	double t1,t2;
        	t1=(f3ab*f1cd-f3cd*f2)/(f1ab*f1cd-f2*f2);
        	t2=(f3cd*f1ab-f2*f3ab)/(f2*f2-f1ab*f1cd);
        	if(0<=t1 && t1 <=1 && 0<=t2 && t2<=1)
        	{
        		Vector3d m,n;
        		m=t1*(b-a)+a;
        		n= t2*(d-c)+c;
        		distance=norm(m-n);
        	}
        	else
        	{
        		distance=std::min(fsc(a,c,d),fsc(b,c,d));
        		distance=std::min(distance,fsc(c,a,b));
        		distance=std::min(distance,fsc(d,a,b));
        	}
        	return distance;
        }


        bool checkcollision::sphere_cell_collision(Vector3d s1,Vector3d c1,Vector3d c2,double r1, double b2)
        {
        	bool flag=0;
        	double d=fsc(s1,c1,c2);
        	if(d>=b2/2+r1)
        		flag=1;
        	return flag;
        }

        bool checkcollision::sphere_collision(Vector3d s1,Vector3d s2, double r1,double r2)
        {
        	bool flag=0;
        	Vector3d dis=s1-s2;
        	double distance= dis.norm();
        	double bound=r1+r2;
        	if(distance>=bound)
        		flag=1;
        	return flag;
        }
        void checkcollision::cal_cord()
        {
        	cord.clear();
        	Vector3d ma(0,0,0);
        	cord.push_back(ma);
        	cord.push_back(p1);
        	cord.push_back(p2);
        	cord.push_back(p1+rot_matrix(check_position.at(0),check_position.at(1),check_position.at(2))*lre.at(1));
        	cord.push_back(p2+rot_matrix(check_position.at(4),check_position.at(5),check_position.at(6))*lre.at(2));
        	cord.push_back(cord.at(3)+rot_matrix(check_position.at(0),check_position.at(1),check_position.at(2))*rot_matrix(check_position.at(3),3)*lre.at(3));
        	cord.push_back(cord.at(4)+rot_matrix(check_position.at(4),check_position.at(5),check_position.at(6))*rot_matrix(check_position.at(7),2)*lre.at(4));
           // ROS_WARN("sizeof cord =%d",cord.size());
        }



int main(int argc, char** argv)
{
      ros::init( argc, argv, "collision_check_node" );
       ros::NodeHandle nh;
       checkcollision checkco(nh);
       checkco.prepare();
      ros::spin();
      return 0;
}
