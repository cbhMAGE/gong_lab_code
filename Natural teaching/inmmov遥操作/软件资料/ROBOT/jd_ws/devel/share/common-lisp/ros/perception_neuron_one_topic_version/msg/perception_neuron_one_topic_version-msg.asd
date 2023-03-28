
(cl:in-package :asdf)

(defsystem "perception_neuron_one_topic_version-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils :actionlib_msgs-msg
               :sensor_msgs-msg
               :std_msgs-msg
)
  :components ((:file "_package")
    (:file "anglegoalAction" :depends-on ("_package_anglegoalAction"))
    (:file "_package_anglegoalAction" :depends-on ("_package"))
    (:file "anglegoalActionGoal" :depends-on ("_package_anglegoalActionGoal"))
    (:file "_package_anglegoalActionGoal" :depends-on ("_package"))
    (:file "anglegoalActionFeedback" :depends-on ("_package_anglegoalActionFeedback"))
    (:file "_package_anglegoalActionFeedback" :depends-on ("_package"))
    (:file "anglegoalGoal" :depends-on ("_package_anglegoalGoal"))
    (:file "_package_anglegoalGoal" :depends-on ("_package"))
    (:file "anglegoalActionResult" :depends-on ("_package_anglegoalActionResult"))
    (:file "_package_anglegoalActionResult" :depends-on ("_package"))
    (:file "anglegoalFeedback" :depends-on ("_package_anglegoalFeedback"))
    (:file "_package_anglegoalFeedback" :depends-on ("_package"))
    (:file "anglegoalResult" :depends-on ("_package_anglegoalResult"))
    (:file "_package_anglegoalResult" :depends-on ("_package"))
  ))