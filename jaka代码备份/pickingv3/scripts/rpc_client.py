from janus import T
import rospy
import std_srvs.srv
import time

rospy.init_node("client", anonymous=True)

req = std_srvs.srv.SetBoolRequest()
srv = rospy.ServiceProxy("rpc_demo", std_srvs.srv.SetBool)

total_cost = 0
N = 1000
for i in range(N):
    t = time.time()
    srv.call(req)
    total_cost += time.time() - t
print(f"cost {total_cost / N * 1000.0:.2f} ms")