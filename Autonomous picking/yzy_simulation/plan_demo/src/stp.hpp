//
// Created by yzy on 2022/2/13.
//

#ifndef PLAN_DEMO_STP_HPP
#define PLAN_DEMO_STP_HPP

#include <ompl/base/Planner.h>

namespace ob = ompl::base;


namespace ompl {
    class STP : public base::Planner {
    private:

    public:
        STP(const base::SpaceInformationPtr &si) : base::Planner(si, "STP") {
            printf("stp construct\n");
        }

        void project(const base::State *st, Eigen::Ref<Eigen::VectorXi> coord) {}

        base::PlannerStatus solve(const base::PlannerTerminationCondition &ptc) override {
            // make sure the planner is configured correctly; ompl::base::Planner::checkValidity
            // ensures that there is at least one input state and a ompl::base::Goal object specified
            printf("stp solve\n");

            checkValidity();
            // get a handle to the Goal from the ompl::base::ProblemDefinition member, pdef_
//            base::Goal *goal = pdef_->getGoal().get();

            // get input states with PlannerInputStates helper, pis_
            // Add the valid start states as milestones
            if (const base::State *st = pis_.nextStart()) {

            }
//                startM_.push_back(addMilestone(si_->cloneState(st)));
//
//            if (startM_.empty())
//            {
//                OMPL_ERROR("%s: There are no valid initial states!", getName().c_str());
//                return base::PlannerStatus::INVALID_START;
//            }

            // if needed, sample states from the goal region (and wait until a state is sampled)
//            const base::State *st = pis_.nextGoal(ptc);
            // or sample a new goal state only if available:
            const base::State *st = pis_.nextGoal();

            // periodically check if ptc() returns true.
            // if it does, terminate planning.
            while (!ptc()) {
                // Start planning here.

                // call routines from SpaceInformation (si_) as needed. i.e.,
                // si_->allocStateSampler() for sampling,
                // si_->checkMotion(state1, state2) for state validity, etc...

                // use the Goal pointer to evaluate whether a sampled state satisfies the goal requirements

                // use log macros for informative messaging, i.e., logInfo("Planner found a solution!");
            }

            // When a solution path is computed, save it here
//            pdef_->addSolutionPath(...);

            // Return a value from the PlannerStatus enumeration.
            // See ompl::base::PlannerStatus for the possible return values
            return base::PlannerStatus::EXACT_SOLUTION;
        }

        void clear() override {
            printf("stp clear\n");

            Planner::clear();
            // clear the data structures here
        }

        // optional, if additional setup/configuration is needed, the setup() method can be implemented
        void setup() override {
            printf("stp setup\n");

            Planner::setup();
            // perhaps attempt some auto-configuration
//            SelfConfig sc(si_, getName());
//            sc.configure...
        }

        void getPlannerData(base::PlannerData &data) const override {
            printf("stp getPlannerData\n");
            // fill data with the states and edges that were created
            // in the exploration data structure
            // perhaps also fill control::PlannerData
        }

    };
}

#endif //PLAN_DEMO_STP_HPP
