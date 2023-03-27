import rospy
import std_srvs.srv

def handler(req):
    return std_srvs.srv.SetBoolResponse()

rospy.init_node("aa", anonymous=True)

s = rospy.Service("rpc_demo", std_srvs.srv.SetBool, handler)
rospy.spin()
