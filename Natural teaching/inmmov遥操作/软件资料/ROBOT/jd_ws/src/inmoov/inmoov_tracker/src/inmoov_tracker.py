#!/usr/bin/env python
# -*- coding: utf-8 -*-

import rospy
import moveit_commander

from moveit_commander import MoveGroupCommander
from trajectory_msgs.msg import JointTrajectoryPoint
from geometry_msgs.msg import PoseStamped, Pose, PointStamped
from visualization_msgs.msg import Marker
from sensor_msgs.msg import JointState
import tf
from tf.transformations import quaternion_from_euler
from scipy.spatial.distance import euclidean 
import shlex, subprocess
import os
from math import sqrt, acos

from geometry_msgs.msg import PointStamped

GROUP_NAME_ARM = 'l_arm' #主要的规划group是左臂。
REFERENCE_FRAME = 'base_link' #主参考系为底部的支撑link

class ArmTracker:
    def __init__(self):
        rospy.init_node('arm_tracker') #节点名称。

        rospy.on_shutdown(self.shutdown)

        robot = moveit_commander.RobotCommander() #创建一个lr1的机器人，让它好连接在一起。
        scene = moveit_commander.PlanningSceneInterface() #引入规划场景。

        # Distance between the last target and the new target before we move the arm
        self.last_target_threshold = 0.1
        
        # Distance between target and end-effector before we move the arm
        self.target_ee_threshold = 0.05
        
        rospy.sleep(10)
        # Initialize the move group for the right arm
        self.left_arm = moveit_commander.MoveGroupCommander(GROUP_NAME_ARM) #初始化group
        
        # Set the reference frame for pose targets
        self.reference_frame = REFERENCE_FRAME
        
        self.target = PoseStamped()
        # Keep track of the last target pose
        self.last_target_pose = PoseStamped() 
        
        # Set the left arm reference frame accordingly
        self.left_arm.set_pose_reference_frame(self.reference_frame)
                        
        # Allow replanning to increase the chances of a solution
        self.left_arm.allow_replanning(False)
                
        # Set a position tolerance in meters
        self.left_arm.set_goal_position_tolerance(0.05)
        
        # Set an orientation tolerance in radians
        self.left_arm.set_goal_orientation_tolerance(3)
        
        # What is the end effector link?
        self.ee_link = self.left_arm.get_end_effector_link() #如果它可以正常启动，那应该可以得到我们的left_arm_end_frame
        
        # Create the transform listener
        self.listener = tf.TransformListener()
        
        # Queue up some tf data...
        rospy.sleep(10)
        rospy.logwarn("wait for messege!")

        # Subscribe to the target topic
        rospy.wait_for_message('/Target_point', PointStamped) #将目标的topic修改为tomatomessage，并用marker形式。

        # Use queue_size=1 so we don't pile up outdated target messages 调用的回调函数是update_target_pose
        self.target_subscriber = rospy.Subscriber('/Target_point', PointStamped, self.update_target_pose, queue_size=1)
        
        rospy.logwarn("Ready for action!")
        
       
    def update_target_pose(self, PointStamped):
        flag = 1
        rospy.loginfo("I see the tomato")
        self.target.header = PointStamped.header #把从相机得到的marker传给target。
        self.target.pose.position = PointStamped.point
        rospy.loginfo(self.target.header) #打印出得到的目标的frame id(应为right_camera_frame)
        
         # Timestamp the target with the current time
        self.target.header.stamp = rospy.Time()
            
          
        # Transform the pose to the base reference frame
        target_base = self.listener.transformPose(self.reference_frame, self.target)
        rospy.loginfo("Transformation succeed")
        rospy.loginfo(target_base) #让我看一下得到的经过tf转换之后的pose
            
        # Compute the distance between the current target and the last target 比较和上一个target之间的距离。
        p1 = [target_base.pose.position.x, target_base.pose.position.y, target_base.pose.position.z]
        p2 = [self.last_target_pose.pose.position.x, self.last_target_pose.pose.position.y, self.last_target_pose.pose.position.z]
                    
        dist_last_target = euclidean(p1, p2)
            
        # Move the arm only if we are far enough away from the previous target
        if dist_last_target < self.last_target_threshold:
            rospy.loginfo("Still close to last target")
            rospy.sleep(0.5)
            flag = 0
            #此处需要一个跳出程序.
            
        # Get the pose of the end effector in the base reference frame
        ee_pose = self.left_arm.get_current_pose(self.ee_link)
            
        # Convert the position values to a Python list
        p3 = [ee_pose.pose.position.x, ee_pose.pose.position.y, ee_pose.pose.position.z]
            
        # Compute the distance between the target and the end-effector
        dist_target = euclidean(p1, p3)
            
        # Only move the arm if we are far enough away from the target
        if dist_target < self.target_ee_threshold:
            rospy.loginfo("Already close enough to target")
            rospy.sleep(1)
            flag = 0

        # Update the current start state
        self.left_arm.set_start_state_to_current_state()
        
        if flag == 1:
            target_base.pose.orientation.x = 0
            target_base.pose.orientation.y = 0  
            self.left_arm.set_pose_target(target_base, self.ee_link) #把目标设置成末端执行器新的Pose.
	    plan = self.left_arm.plan()
	    rospy.loginfo(plan)	
            success = self.left_arm.go()
            
        if success:
            # Store the current target as the last target
            self.last_target_pose = target.base
            
            # Pause a bit between motions to keep from locking up
            rospy.sleep(0.5)
            
                    
    def relax_all_servos(self):
        pass #关闭所有的电机。
           
    def shutdown(self):
        # Stop any further target messages from being processed
        self.target_subscriber.unregister()
        
        # Stop any current arm movement
        self.left_arm.stop()
        
        # Move to the resting position
        self.left_arm.set_named_target('resting')
        self.left_arm.go()
        
        # Relax the servos
        self.relax_all_servos()
        rospy.logwarn("Shut down!")

        os._exit(0) 
        
if __name__ == "__main__":
    try:
        ArmTracker()
        rospy.spin()
    except rospy.ROSInterruptException:
        rospy.loginfo("Arm tracker node terminated.")
    
