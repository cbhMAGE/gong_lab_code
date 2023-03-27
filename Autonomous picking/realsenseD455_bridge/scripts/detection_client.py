#! /usr/bin/env python

import sys
from this import d
import rospy
from pickingv2.srv import *
from sensor_msgs.msg import Image
import sensor_msgs.msg
from cv_bridge import CvBridge, CvBridgeError
from copy import deepcopy
import numpy as np
from scipy.spatial.transform.rotation import Rotation as R
import cv2
import message_filters
import tf
from moveit_tutorials.msg import tomatos_msg

class Point:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self._xyz = np.array((x, y, z), dtype=np.double)

    @staticmethod
    def build_from_homo(homo: np.ndarray):
        return Point(*homo.reshape(-1)[:3])

    @property
    def x(self) -> np.double:
        return self._xyz[0]

    @property
    def y(self) -> np.double:
        return self._xyz[1]

    @property
    def z(self) -> np.double:
        return self._xyz[2]

    def to_homo(self) -> np.ndarray:
        return np.append(self._xyz, 1).reshape((4, 1))

    def to_mat4x4(self) -> np.ndarray:
        mat = np.eye(4, dtype=np.double)
        mat[:3, -1] = self._xyz
        return mat

    def to_msg_point(self) -> geometry_msgs.msg.Point:
        msg = geometry_msgs.msg.Point()
        msg.x = self.x
        msg.y = self.y
        msg.z = self.z
        return msg
    
    def length(self)->float:
        return np.linalg.norm(self._xyz)

    def __getitem__(self, index: int) -> np.double:
        return self._xyz[index]

    def __str__(self):
        return f'Point({self.x:.3f}, {self.y:.3f}, {self.z:.3f})'

    def __repr__(self):
        return self.__str__()

    def __mul__(self, other) -> 'Point':
        if isinstance(other, float):
            tmp = self._xyz * other
            return Point(*tmp)
        else:
            raise TypeError('a float is needed')

    def __add__(self, other: 'Point') -> 'Point':
        return Point(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Point') -> 'Point':
        return Point(self.x - other.x, self.y - other.y, self.z - other.z)


class RGBSubscriber(object):
    def __init__(self, pos_pub: rospy.Publisher) -> None:
        self.color_react_sub = message_filters.Subscriber("/kinect2/hd/image_color_rect", sensor_msgs.msg.Image)
        self.depth_react_sub = message_filters.Subscriber("/kinect2/hd/image_depth_rect", sensor_msgs.msg.Image)
        self.ts = message_filters.TimeSynchronizer([self.color_react_sub, self.depth_react_sub], 10)
        # tfListener = tf.TransformListener()
        self.trans=[0.348114, 0.368521, 0.143299]
        self.rot =  [0.00158355, -0.51535, 0.856448, -0.0301528]

        # listener = tf.TransformListener()
        # (trans,rot) = listener.lookupTransform('/platform', '/kinect2_rgb_optical_frame', rospy.Time(0))
        # print(trans, rot)
        self.rotate = R.from_quat(self.rot).as_matrix()
        # self.rotate
        self.Matrix = np.zeros((4,4), dtype=np.float32)
        self.Matrix[0,0] = self.rotate[0,0]
        self.Matrix[0,1] = self.rotate[0,1]
        self.Matrix[0,2] = self.rotate[0,2]
        self.Matrix[1,0] = self.rotate[1,0]
        self.Matrix[1,1] = self.rotate[1,1]
        self.Matrix[1,2] = self.rotate[1,2]
        self.Matrix[2,0] = self.rotate[2,0]
        self.Matrix[2,1] = self.rotate[2,1]
        self.Matrix[2,2] = self.rotate[2,2]
        self.Matrix[0,3] = self.trans[0]
        self.Matrix[1,3] = self.trans[1]
        self.Matrix[2,3] = self.trans[2]
        self.pos_pub = pos_pub
        print("dasda: ", np.linalg.det(self.Matrix))
        self.ts.registerCallback(self.callback)
        


    def depth_fill(self, x, y, depth_img):
        seek_step = 20
        def get_left(_x, _y, _depth_img):
            left_pixel = _x
            while (left_pixel > 0) and (_depth_img[_y, left_pixel] == 0) and (left_pixel > _x - seek_step):
                left_pixel = left_pixel - 1
            return _depth_img[_y, left_pixel]

        def get_right(_x, _y, _depth_img):
            right_pixel = _x
            while (right_pixel < 1920) and (_depth_img[_y, right_pixel] == 0) and (right_pixel < _x + seek_step):
                right_pixel = right_pixel + 1
            return _depth_img[_y, right_pixel]

        def get_top(_x, _y, _depth_img):
            top_pixel = _y
            while (top_pixel > 0) and (_depth_img[top_pixel, _x] == 0) and (top_pixel > _y - seek_step):
                top_pixel = top_pixel - 1
            return _depth_img[top_pixel, _x]

        def get_bottom(_x, _y, _depth_img):
            bottom_pixel = _y
            while (bottom_pixel < 1080) and (_depth_img[bottom_pixel, _x] == 0) and (bottom_pixel < _y + seek_step):
                bottom_pixel = bottom_pixel + 1
            return _depth_img[bottom_pixel, _x]

        if not (0 <= y < 1080 and 0 <= x < 1920):
            return 0
        z = depth_img[y, x]
        available = 0
        res = 0
        if z == 0:
            left = get_left(x, y, depth_img)
            right = get_right(x, y, depth_img)
            top = get_top(x, y, depth_img)
            bottom = get_bottom(x, y, depth_img)
            for dep in [left, right, top, bottom]:
                if dep != 0:
                    res = res + dep
                    available = available + 1

            z = res / available if available != 0 else 0
            # print(left, right, top, bottom)
        else:
            z = depth_img[y, x]
        return z
    

# [1087.3735327421248, 0.0, 961.3400868419684, 0.0, 0.0, 1087.5876546027164, 531.6127973518466, 0.0, 0.0, 0.0, 1.0, 0.0]
    def convert_pixel_to_world(self, d, pixel_pt: Point):
        x, y = pixel_pt.x, pixel_pt.y
        # d = depth[int(y), int(x)]
        fx, fy = 1087.3735327421248, 1087.5876546027164
        cx, cy = 961.3400868419684, 531.6127973518466
        world_x = (x - cx) / fx * d
        world_y = (y - cy) / fy * d
        return [world_x, world_y, float(d)]

    def convert_target_to_world(self, d, pixel_pt: Point):
        x, y, z = self.convert_pixel_to_world(d, pixel_pt)
        return [x,y,z]

    def callback(self, color: sensor_msgs.msg.Image, depth: sensor_msgs.msg.Image):
        assert isinstance(color, Image)
        # gen=point_cloud2.read_points(msg,field_names=("x","y","z","rgb"))
        rospy.wait_for_service("/target_detection_srv")
        detection_client = rospy.ServiceProxy("/target_detection_srv", TargetDetectionSrv)
        response = detection_client(color)
        
        cv2_color_img = CvBridge().imgmsg_to_cv2(response.result_img)
        cv2_depth_img = CvBridge().imgmsg_to_cv2(depth)

        targets = []
        _tomatos_msg = tomatos_msg()
        _tomatos_msg.frame_id = "/platform"
        _tomatos_msg.num_of_tomatos = 0
        a_list = []
        if response.poses2d:
            for index, pose in enumerate(response.poses2d):
                pose: geometry_msgs.msg.Pose2D = pose
                _d = self.depth_fill(int(pose.x), int(pose.y), cv2_depth_img)
                if _d == 0:
                    continue
                t = self.convert_target_to_world(_d, Point(pose.x, pose.y))
                t = [x/1000 for x in t]
                t.append(1)
                t[2] += 0.026
                res = np.matmul(self.Matrix, np.array(t,dtype=np.float64))
                # _tomatos_msg.poses_x.append(t[0])
                # _tomatos_msg.poses_y.append(t[1]+0.025)
                # _tomatos_msg.poses_z.append(t[2])
                a_list.append([res[0], res[1], res[2]])
                a_list.sort()

                
                _tomatos_msg.num_of_tomatos += 1
                print(t)
                # rospy.loginfo(str(res))
            # global pos_pub
            for res in a_list:
                _tomatos_msg.poses_x.append(res[0])
                _tomatos_msg.poses_y.append(res[1])
                _tomatos_msg.poses_z.append(res[2])
            self.pos_pub.publish(_tomatos_msg)

        else: # Adding tomato Manually
            
            pos_res = [[0.18,-0.22,0.38],
                       [0.29,-0.22,0.53],
                       [0.45,-0.22,0.5],
                       [0.52,-0.22,0.36],
                       [0.85,-0.22,0.43],
                       [0.92,-0.22,0.28]]
            
            _tomatos_msg.num_of_tomatos = len(pos_res)
            
            for i in range(_tomatos_msg.num_of_tomatos):
                
                _tomatos_msg.poses_x.append(pos_res[i][0]-0.12)
                _tomatos_msg.poses_y.append(pos_res[i][1])
                _tomatos_msg.poses_z.append(pos_res[i][2])
            self.pos_pub.publish(_tomatos_msg)
                
        # cv2.imshow("window", cv2_color_img)
        # cv2.waitKey(0)


def main():
    rospy.init_node("detection_client")
    pos_pub = rospy.Publisher("/tomato_poses", tomatos_msg, queue_size=10)
    RGBSubscriber(pos_pub)
    rospy.spin()

if __name__ == "__main__":
    main()
