//
// Created by yzy on 2022/2/13.
//

#include <iostream>
#include <vector>
#include <chrono>
#include <ros/ros.h>
#include <moveit_msgs/GetStateValidity.h>
#include <moveit_msgs/DisplayTrajectory.h>
#include <moveit_msgs/RobotTrajectory.h>

#include <ompl/base/StateSpace.h>
#include <ompl/base/SpaceInformation.h>
#include <ompl/base/spaces/RealVectorStateSpace.h>
#include <ompl/base/spaces/RealVectorBounds.h>
#include <ompl/geometric/PathGeometric.h>
#include <ompl/geometric/SimpleSetup.h>
#include <ompl/geometric/planners/prm/PRM.h>

#include "stp.hpp"


namespace ob = ompl::base;
namespace og = ompl::geometric;

class Timer {
private:
    std::chrono::high_resolution_clock::time_point m_t;
    std::string m_str;
public:
    explicit Timer(const std::string &name) {
        m_t = std::chrono::high_resolution_clock::now();
        m_str = name;
    }

    ~Timer() {
        auto cost = std::chrono::high_resolution_clock::now() - m_t;
        std::chrono::duration<double, std::ratio<1, 1000>> duration_ms = std::chrono::duration_cast<
                std::chrono::duration<double, std::ratio<1, 1000>>>(cost);
        printf("[%s] cost %.2f ms\n", m_str.c_str(), duration_ms.count());
    }
};

class RosTool {
private:
    ros::NodeHandle m_nh;
    ros::ServiceClient m_stateValidityClient;
    ros::Publisher m_trajectoryPub;

public:
    explicit RosTool(ros::NodeHandle &nh) : m_nh(nh) {
        m_stateValidityClient = m_nh.serviceClient<moveit_msgs::GetStateValidity>("check_state_validity");
        m_trajectoryPub = m_nh.advertise<moveit_msgs::DisplayTrajectory>("move_group/display_planned_path", 5);
    }

    bool checkValidity(const std::vector<double> &jVals) {
        moveit_msgs::GetStateValidity msg;
        auto &req = msg.request;
        req.group_name = "arm";
        req.robot_state.joint_state.name.emplace_back("joint_1");
        req.robot_state.joint_state.name.emplace_back("joint_2");
        req.robot_state.joint_state.name.emplace_back("joint_3");
        for (auto val: jVals) {
            req.robot_state.joint_state.position.emplace_back(val);
        }
        if (m_stateValidityClient.call(msg)) {
            return msg.response.valid;
        } else {
            ROS_ERROR("Failed to call service /check_state_validity");
            return false;
        }
    }

    void publishTrajectory(og::PathGeometric &trajectory) {
        moveit_msgs::RobotTrajectory trajectoryMsg;
        trajectoryMsg.joint_trajectory.joint_names.emplace_back("joint_1");
        trajectoryMsg.joint_trajectory.joint_names.emplace_back("joint_2");
        trajectoryMsg.joint_trajectory.joint_names.emplace_back("joint_3");
        double time = 5.0 / (double) trajectory.getStateCount();
        for (int i = 0; i < trajectory.getStateCount(); ++i) {
            auto state = trajectory.getState(i);
            const auto *sDate = state->as<ob::RealVectorStateSpace::StateType>();
            trajectory_msgs::JointTrajectoryPoint pt;
            pt.positions.emplace_back(sDate->values[0]);
            pt.positions.emplace_back(sDate->values[1]);
            pt.positions.emplace_back(sDate->values[2]);
            pt.time_from_start.fromSec(time * i);
            trajectoryMsg.joint_trajectory.points.emplace_back(pt);
        }
        moveit_msgs::DisplayTrajectory msg;
        msg.trajectory.emplace_back(trajectoryMsg);
        m_trajectoryPub.publish(msg);
    }
};

int main(int argc, char **argv) {
    ros::init(argc, argv, "planar_demo_node");
    ros::NodeHandle nh;

    RosTool rosTool(nh);
//    bool res;
//
//    {
//        Timer timer("checkValidity");
//        for (int i = 0; i < 100; ++i) {
//            res = rosTool.checkValidity({0, 0, 0});
//        }
//    }

    auto space(std::make_shared<ob::RealVectorStateSpace>(3));
    ob::RealVectorBounds bounds(3);
    bounds.setLow(-M_PI);
    bounds.setHigh(M_PI);
    space->setBounds(bounds);
    og::SimpleSetup ss(space);
    ss.setStateValidityChecker([&](const ob::State *state) -> bool {
        const auto *s = state->as<ob::RealVectorStateSpace::StateType>();
        return rosTool.checkValidity({s->values[0], s->values[1], s->values[2]});
    });

    ob::ScopedState<> start(space), goal(space);

    start[0] = 0;
    start[1] = 0;
    start[2] = 0;

    goal[0] = -M_PI_2;
    goal[1] = 0.0;
    goal[2] = 0.0;

    ss.setStartAndGoalStates(start, goal);

//    ob::PlannerPtr prmPlanner(std::make_shared<og::PRM>(ss.getSpaceInformation()));
    ob::PlannerPtr stpPlanner(std::make_shared<ompl::STP>(ss.getSpaceInformation()));

    ss.setPlanner(stpPlanner);

    ob::PlannerStatus solved = ss.solve(60.0);

//    if (solved) {
//        std::cout << "Found solution:" << std::endl;
////        ss.simplifySolution();
//        // print the path to screen
//        ss.getSolutionPath().print(std::cout);
//        rosTool.publishTrajectory(ss.getSolutionPath());
//    }

//    std::cout << std::boolalpha << res << std::endl;
    return 0;
}