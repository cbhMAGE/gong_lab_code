# CMake generated Testfile for 
# Source directory: /home/pn/jd_ws/src/moveit/moveit_ros/visualization
# Build directory: /home/pn/jd_ws/build/moveit/moveit_ros/visualization
# 
# This file includes the relevant testing commands required for 
# testing this directory and lists subdirectories to be tested as well.
ADD_TEST(_ctest_moveit_ros_visualization_rostest_test_moveit_joy.test "/home/pn/jd_ws/build/catkin_generated/env_cached.sh" "/usr/bin/python" "/opt/ros/indigo/share/catkin/cmake/test/run_tests.py" "/home/pn/jd_ws/build/test_results/moveit_ros_visualization/rostest-test_moveit_joy.xml" "--return-code" "/opt/ros/indigo/share/rostest/cmake/../../../bin/rostest --pkgdir=/home/pn/jd_ws/src/moveit/moveit_ros/visualization --package=moveit_ros_visualization --results-filename test_moveit_joy.xml --results-base-dir \"/home/pn/jd_ws/build/test_results\" /home/pn/jd_ws/src/moveit/moveit_ros/visualization/test/moveit_joy.test ")
SUBDIRS(rviz_plugin_render_tools)
SUBDIRS(robot_state_rviz_plugin)
SUBDIRS(planning_scene_rviz_plugin)
SUBDIRS(motion_planning_rviz_plugin)
SUBDIRS(trajectory_rviz_plugin)
