// Generated by gencpp from file moveit_msgs/ExecuteTrajectoryFeedback.msg
// DO NOT EDIT!


#ifndef MOVEIT_MSGS_MESSAGE_EXECUTETRAJECTORYFEEDBACK_H
#define MOVEIT_MSGS_MESSAGE_EXECUTETRAJECTORYFEEDBACK_H


#include <string>
#include <vector>
#include <map>

#include <ros/types.h>
#include <ros/serialization.h>
#include <ros/builtin_message_traits.h>
#include <ros/message_operations.h>


namespace moveit_msgs
{
template <class ContainerAllocator>
struct ExecuteTrajectoryFeedback_
{
  typedef ExecuteTrajectoryFeedback_<ContainerAllocator> Type;

  ExecuteTrajectoryFeedback_()
    : state()  {
    }
  ExecuteTrajectoryFeedback_(const ContainerAllocator& _alloc)
    : state(_alloc)  {
  (void)_alloc;
    }



   typedef std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other >  _state_type;
  _state_type state;




  typedef boost::shared_ptr< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> > Ptr;
  typedef boost::shared_ptr< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> const> ConstPtr;

}; // struct ExecuteTrajectoryFeedback_

typedef ::moveit_msgs::ExecuteTrajectoryFeedback_<std::allocator<void> > ExecuteTrajectoryFeedback;

typedef boost::shared_ptr< ::moveit_msgs::ExecuteTrajectoryFeedback > ExecuteTrajectoryFeedbackPtr;
typedef boost::shared_ptr< ::moveit_msgs::ExecuteTrajectoryFeedback const> ExecuteTrajectoryFeedbackConstPtr;

// constants requiring out of line definition



template<typename ContainerAllocator>
std::ostream& operator<<(std::ostream& s, const ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> & v)
{
ros::message_operations::Printer< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >::stream(s, "", v);
return s;
}

} // namespace moveit_msgs

namespace ros
{
namespace message_traits
{



// BOOLTRAITS {'IsFixedSize': False, 'IsMessage': True, 'HasHeader': False}
// {'shape_msgs': ['/opt/ros/indigo/share/shape_msgs/cmake/../msg'], 'std_msgs': ['/opt/ros/indigo/share/std_msgs/cmake/../msg'], 'moveit_msgs': ['/home/pn/jd_ws/devel/share/moveit_msgs/msg', '/home/pn/jd_ws/src/moveit_msgs/msg'], 'trajectory_msgs': ['/opt/ros/indigo/share/trajectory_msgs/cmake/../msg'], 'sensor_msgs': ['/opt/ros/indigo/share/sensor_msgs/cmake/../msg'], 'object_recognition_msgs': ['/opt/ros/indigo/share/object_recognition_msgs/cmake/../msg'], 'octomap_msgs': ['/opt/ros/indigo/share/octomap_msgs/cmake/../msg'], 'geometry_msgs': ['/opt/ros/indigo/share/geometry_msgs/cmake/../msg'], 'actionlib_msgs': ['/opt/ros/indigo/share/actionlib_msgs/cmake/../msg']}

// !!!!!!!!!!! ['__class__', '__delattr__', '__dict__', '__doc__', '__eq__', '__format__', '__getattribute__', '__hash__', '__init__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', '_parsed_fields', 'constants', 'fields', 'full_name', 'has_header', 'header_present', 'names', 'package', 'parsed_fields', 'short_name', 'text', 'types']




template <class ContainerAllocator>
struct IsFixedSize< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct IsFixedSize< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> const>
  : FalseType
  { };

template <class ContainerAllocator>
struct IsMessage< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
  : TrueType
  { };

template <class ContainerAllocator>
struct IsMessage< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> const>
  : TrueType
  { };

template <class ContainerAllocator>
struct HasHeader< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
  : FalseType
  { };

template <class ContainerAllocator>
struct HasHeader< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> const>
  : FalseType
  { };


template<class ContainerAllocator>
struct MD5Sum< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "af6d3a99f0fbeb66d3248fa4b3e675fb";
  }

  static const char* value(const ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator>&) { return value(); }
  static const uint64_t static_value1 = 0xaf6d3a99f0fbeb66ULL;
  static const uint64_t static_value2 = 0xd3248fa4b3e675fbULL;
};

template<class ContainerAllocator>
struct DataType< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "moveit_msgs/ExecuteTrajectoryFeedback";
  }

  static const char* value(const ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator>&) { return value(); }
};

template<class ContainerAllocator>
struct Definition< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
{
  static const char* value()
  {
    return "# ====== DO NOT MODIFY! AUTOGENERATED FROM AN ACTION DEFINITION ======\n\
\n\
# The internal state that the move group action currently is in\n\
string state\n\
\n\
";
  }

  static const char* value(const ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator>&) { return value(); }
};

} // namespace message_traits
} // namespace ros

namespace ros
{
namespace serialization
{

  template<class ContainerAllocator> struct Serializer< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
  {
    template<typename Stream, typename T> inline static void allInOne(Stream& stream, T m)
    {
      stream.next(m.state);
    }

    ROS_DECLARE_ALLINONE_SERIALIZER
  }; // struct ExecuteTrajectoryFeedback_

} // namespace serialization
} // namespace ros

namespace ros
{
namespace message_operations
{

template<class ContainerAllocator>
struct Printer< ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator> >
{
  template<typename Stream> static void stream(Stream& s, const std::string& indent, const ::moveit_msgs::ExecuteTrajectoryFeedback_<ContainerAllocator>& v)
  {
    s << indent << "state: ";
    Printer<std::basic_string<char, std::char_traits<char>, typename ContainerAllocator::template rebind<char>::other > >::stream(s, indent + "  ", v.state);
  }
};

} // namespace message_operations
} // namespace ros

#endif // MOVEIT_MSGS_MESSAGE_EXECUTETRAJECTORYFEEDBACK_H
