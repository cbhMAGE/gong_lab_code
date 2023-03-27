/*
create by Zhiyu YANG at 2021/11/07
*/

#include <kdl/velocityprofile_spline.hpp>
#include <ros/ros.h>
#include <trajectory_msgs/JointTrajectory.h>
#include <pickingv2/PickingTrajectoryFilter.h>

bool interpolatePt(trajectory_msgs::JointTrajectoryPoint &p1,
                   trajectory_msgs::JointTrajectoryPoint &p2, double time_from_start,
                   trajectory_msgs::JointTrajectoryPoint &interp_pt) {
    bool rtn = false;
    double p1_time_from_start = p1.time_from_start.toSec();
    double p2_time_from_start = p2.time_from_start.toSec();

    ROS_DEBUG_STREAM("time from start: " << time_from_start);

    if (time_from_start >= p1_time_from_start && time_from_start <= p2_time_from_start) {
        if (p1.positions.size() == p1.velocities.size() && p1.positions.size() == p1.accelerations.size()) {
            if (p1.positions.size() == p2.positions.size() && p1.velocities.size() == p2.velocities.size()
                && p1.accelerations.size() == p2.accelerations.size()) {
                // Copy p1 to ensure the interp_pt has the correct size vectors
                interp_pt = p1;
                // TODO: Creating a new spline calculator in this function means that
                // it may be created multiple times for the same points (assuming the
                // resample duration is less that the actual duration, which it might
                // be sometimes)
                KDL::VelocityProfile_Spline spline_calc;
                ROS_DEBUG_STREAM("---------------Begin interpolating joint point---------------");

                for (size_t i = 0; i < p1.positions.size(); ++i) {
                    // Calculated relative times for spline calculation
                    double time_from_p1 = time_from_start - p1.time_from_start.toSec();
                    double time_from_p1_to_p2 = p2_time_from_start - p1_time_from_start;

                    ROS_DEBUG_STREAM("time from p1: " << time_from_p1);
                    ROS_DEBUG_STREAM("time_from_p1_to_p2: " << time_from_p1_to_p2);

                    spline_calc.SetProfileDuration(p1.positions[i], p1.velocities[i], p1.accelerations[i],
                                                   p2.positions[i],
                                                   p2.velocities[i], p2.accelerations[i], time_from_p1_to_p2);

                    ros::Duration time_from_start_dur(time_from_start);
                    ROS_DEBUG_STREAM("time from start_dur: " << time_from_start_dur);

                    interp_pt.time_from_start = time_from_start_dur;
                    interp_pt.positions[i] = spline_calc.Pos(time_from_p1);
                    interp_pt.velocities[i] = spline_calc.Vel(time_from_p1);
                    interp_pt.accelerations[i] = spline_calc.Acc(time_from_p1);

                    ROS_DEBUG_STREAM(
                            "p1.pos: " << p1.positions[i] << ", vel: " << p1.velocities[i] << ", acc: "
                                       << p1.accelerations[i] << ", tfs: " << p1.time_from_start);

                    ROS_DEBUG_STREAM(
                            "p2.pos: " << p2.positions[i] << ", vel: " << p2.velocities[i] << ", acc: "
                                       << p2.accelerations[i] << ", tfs: " << p2.time_from_start);

                    ROS_DEBUG_STREAM(
                            "interp_pt.pos: " << interp_pt.positions[i] << ", vel: " << interp_pt.velocities[i]
                                              << ", acc: " << interp_pt.accelerations[i] << ", tfs: "
                                              << interp_pt.time_from_start);
                }
                ROS_DEBUG_STREAM("---------------End interpolating joint point---------------");
                rtn = true;
            } else {
                ROS_ERROR_STREAM("Trajectory point size mismatch");
                ROS_ERROR_STREAM(
                        "Trajectory point 1, pos: " << p1.positions.size() << " vel: " << p1.velocities.size()
                                                    << " acc: " << p1.accelerations.size());
                ROS_ERROR_STREAM(
                        "Trajectory point 2, pos: " << p2.positions.size() << " vel: " << p2.velocities.size()
                                                    << " acc: " << p2.accelerations.size());
                rtn = false;
            }

        } else {
            ROS_ERROR_STREAM(
                    "Trajectory point not fully defined, pos: " << p1.positions.size() << " vel: "
                                                                << p1.velocities.size() << " acc: "
                                                                << p1.accelerations.size());
            rtn = false;
        }
    } else {
        ROS_ERROR_STREAM(
                "Time: " << time_from_start << " not between interpolation point times[" << p1.time_from_start.toSec()
                         << "," << p2.time_from_start.toSec() << "]");
        rtn = false;
    }

    return rtn;
}


bool update(const moveit_msgs::RobotTrajectory &trajectory_in, moveit_msgs::RobotTrajectory &trajectory_out,
            double sample_duration_) {
    bool success = false;
    size_t size_in = trajectory_in.joint_trajectory.points.size();
    double duration_in = trajectory_in.joint_trajectory.points.back().time_from_start.toSec();
    double interpolated_time = 0.0;
    size_t index_in = 0;

    trajectory_msgs::JointTrajectoryPoint p1, p2, interp_pt;

    trajectory_out = trajectory_in;

    // Clear out the trajectory points
    trajectory_out.joint_trajectory.points.clear();

    while (interpolated_time < duration_in) {
        ROS_DEBUG_STREAM("Interpolated time: " << interpolated_time);
        // Increment index until the interpolated time is past the start time.
        while (interpolated_time > trajectory_in.joint_trajectory.points[index_in + 1].time_from_start.toSec()) {
            ROS_DEBUG_STREAM(
                    "Interpolated time: " << interpolated_time << ", next point time: "
                                          << (trajectory_in.joint_trajectory.points[index_in +
                                                                                    1].time_from_start.toSec()));
            ROS_DEBUG_STREAM("Incrementing index");
            index_in++;
            if (index_in >= size_in) {
                ROS_ERROR_STREAM(
                        "Programming error, index: " << index_in << ", greater(or equal) to size: " << size_in
                                                     << " input duration: " << duration_in << " interpolated time:)"
                                                     << interpolated_time);
                return false;
            }
        }
        p1 = trajectory_in.joint_trajectory.points[index_in];
        p2 = trajectory_in.joint_trajectory.points[index_in + 1];
        if (!interpolatePt(p1, p2, interpolated_time, interp_pt)) {
            ROS_ERROR_STREAM("Failed to interpolate point");
            return false;
        }
        trajectory_out.joint_trajectory.points.push_back(interp_pt);
        interpolated_time += sample_duration_;

    }

    ROS_INFO_STREAM(
            "Interpolated time exceeds original trajectory (quitting), original: " << duration_in
                                                                                   << " final interpolated time: "
                                                                                   << interpolated_time);
    p2 = trajectory_in.joint_trajectory.points.back();
    p2.time_from_start = ros::Duration(interpolated_time);
    // TODO: Really should check that appending the last point doesn't result in
    // really slow motion at the end.  This could happen if the sample duration is a
    // large percentage of the trajectory duration (not likely).
    trajectory_out.joint_trajectory.points.push_back(p2);

    ROS_INFO_STREAM(
            "Uniform sampling, resample duraction: " << sample_duration_ << " input traj. size: "
                                                     << trajectory_in.joint_trajectory.points.size()
                                                     << " output traj. size: "
                                                     << trajectory_out.joint_trajectory.points.size());

    success = true;
    return success;
}

bool srv_callback(pickingv2::PickingTrajectoryFilter::Request &req,
                  pickingv2::PickingTrajectoryFilter::Response &res) {
    auto ret = update(req.trajectory, res.trajectory, req.sample_duration);
    res.success = ret;
    return true;
}

int main(int argc, char **argv) {
    ros::init(argc, argv, "uniform_sample_filter_srv");
    ros::NodeHandle n;
    ros::ServiceServer service = n.advertiseService(
            "picking/uniform_sample_filter", srv_callback);
    ros::spin();
    return 0;
}