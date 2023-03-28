// Generated by gencpp from file perception_neuron_one_topic_version/anglegoalActionGoal.msg
// DO NOT EDIT!


#ifndef PERCEPTION_NEURON_ONE_TOPIC_VERSION_MESSAGE_ANGLEGOALACTIONGOAL_H
#define PERCEPTION_NEURON_ONE_TOPIC_VERSION_MESSAGE_ANGLEGOALACTIONGOAL_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>

#include <std_msgs/Header.h>
#include <actionlib_msgs/GoalID.h>
#include <perception_neuron_one_topic_version/anglegoalGoal.h>

namespace perception_neuron_one_topic_version
{
template <class ContainerAllocator>
struct anglegoalActionGoal_
{
  typedef anglegoalActionGoal_<ContainerAllocator> Type;

  anglegoalActionGoal_()
    : header()
    , goal_id()
    , goal()  {
    }
  anglegoalActionGoal_(const ContainerAllocator& _alloc)
    : header(_alloc)
    , goal_id(_alloc)
    , goal(_alloc)  {
  (void)_alloc;
    }



   typedef  ::std_msgs::Header_<ContainerAllocator>  _header_type;
  _header_type header;

   typedef  ::actionlib_msgs::GoalID_<ContainerAllocator>  _goal_id_type;
  _goal_id_type goal_id;

   typedef  ::perception_neuron_one_topic_version::anglegoalGoal_<ContainerAllocator>  _goal_type;
  _goal_type goal;




  typedef boost::shared_ptr< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> const> ConstPtr;

}; // struct anglegoalActionGoal_

typedef ::perception_neuron_one_topic_version::anglegoalActionGoal_<std::allocator<void> > anglegoalActionGoal;

typedef boost::shared_ptr< ::perception_neuron_one_topic_version::anglegoalActionGoal > anglegoalActionGoalPtr;
typedef boost::shared_ptr< ::perception_neuron_one_topic_version::anglegoalActionGoal const> anglegoalActionGoalConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >::stream(s, "", v);
return s;
}

} // namespace perception_neuron_one_topic_version

namespace ros
{
namespace message_traits
{



// BOOLTRAITS {'IsFixedSize': False, 'IsMessage': True, 'HasHeader': True}
// {'sensor_msgs': ['/opt/ros/indigo/share/sensor_msgs/cmake/../msg'], 'perception_neuron_one_topic_version': ['/home/pn/jd_ws/devel/share/perception_neuron_one_topic_version/msg'], 'geometry_msgs': ['/opt/ros/indigo/share/geometry_msgs/cmake/../msg'], 'std_msgs': ['/opt/ros/indigo/share/std_msgs/cmake/../msg'], 'actionlib_msgs': ['/opt/ros/indigo/share/actionlib_msgs/cmake/../msg']}

// !!!!!!!!!!! ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_parsed_fields', 'constants', 'fields', 'full_name', 'has_header', 'header_present', 'names', 'package', 'parsed_fields', 'short_name', 'text', 'types']




template <class ContainerAllocator>
struct IsFixedSize< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> const>
  : TrueType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "f57eaa19c0db228fdf8cb31c7cb9351b";
  }

  static const char* value(const ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xf57eaa19c0db228fULL;
  static const uint64_t static_value2 = 0xdf8cb31c7cb9351bULL;
};

template<class ContainerAllocator>
struct DataType< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "perception_neuron_one_topic_version/anglegoalActionGoal";
  }

  static const char* value(const ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n\
\n\
Header header\n\
actionlib_msgs/GoalID goal_id\n\
anglegoalGoal goal\n\
\n\
================================================================================\n\
MSG: std_msgs/Header\n\
# Standard metadata for higher-level stamped data types.\n\
# This is generally used to communicate timestamped data \n\
# in a particular coordinate frame.\n\
# \n\
# sequence ID: consecutively increasing ID \n\
uint32 seq\n\
#Two-integer timestamp that is expressed as:\n\
# * stamp.sec: seconds (stamp_secs) since epoch (in Python the variable is called 'secs')\n\
# * stamp.nsec: nanoseconds since stamp_secs (in Python the variable is called 'nsecs')\n\
# time-handling sugar is provided by the client library\n\
time stamp\n\
#Frame this data is associated with\n\
# 0: no frame\n\
# 1: global frame\n\
string frame_id\n\
\n\
================================================================================\n\
MSG: actionlib_msgs/GoalID\n\
# The stamp should store the time at which this goal was requested.\n\
# It is used by an action server when it tries to preempt all\n\
# goals that were requested before a certain time\n\
time stamp\n\
\n\
# The id provides a way to associate feedback and\n\
# result message with specific goal requests. The id\n\
# specified must be unique.\n\
string id\n\
\n\
\n\
================================================================================\n\
MSG: perception_neuron_one_topic_version/anglegoalGoal\n\
# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n\
#Define the goal \n\
sensor_msgs/JointState jointstate\n\
\n\
\n\
================================================================================\n\
MSG: sensor_msgs/JointState\n\
# This is a message that holds data to describe the state of a set of torque controlled joints. \n\
#\n\
# The state of each joint (revolute or prismatic) is defined by:\n\
#  * the position of the joint (rad or m),\n\
#  * the velocity of the joint (rad/s or m/s) and \n\
#  * the effort that is applied in the joint (Nm or N).\n\
#\n\
# Each joint is uniquely identified by its name\n\
# The header specifies the time at which the joint states were recorded. All the joint states\n\
# in one message have to be recorded at the same time.\n\
#\n\
# This message consists of a multiple arrays, one for each part of the joint state. \n\
# The goal is to make each of the fields optional. When e.g. your joints have no\n\
# effort associated with them, you can leave the effort array empty. \n\
#\n\
# All arrays in this message should have the same size, or be empty.\n\
# This is the only way to uniquely associate the joint name with the correct\n\
# states.\n\
\n\
\n\
Header header\n\
\n\
string[] name\n\
float64[] position\n\
float64[] velocity\n\
float64[] effort\n\
";
  }

  static const char* value(const ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.header);
      stream.next(m.goal_id);
      stream.next(m.goal);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct anglegoalActionGoal_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::perception_neuron_one_topic_version::anglegoalActionGoal_<ContainerAllocator>& v)
  {
    s << indent << "header: ";
    s << std::endl;
    Printer< ::std_msgs::Header_<ContainerAllocator> >::stream(s, indent + "  ", v.header);
    s << indent << "goal_id: ";
    s << std::endl;
    Printer< ::actionlib_msgs::GoalID_<ContainerAllocator> >::stream(s, indent + "  ", v.goal_id);
    s << indent << "goal: ";
    s << std::endl;
    Printer< ::perception_neuron_one_topic_version::anglegoalGoal_<ContainerAllocator> >::stream(s, indent + "  ", v.goal);
  }
};

} // namespace message_operations
} // namespace ros

#endif // PERCEPTION_NEURON_ONE_TOPIC_VERSION_MESSAGE_ANGLEGOALACTIONGOAL_H
