# -*- coding: utf-8 -*-
# How to use iterative closest point
# http://pointclouds.org/documentation/tutorials/iterative_closest_point.php#iterative-closest-point

import pcl
import random
import numpy as np
from rosdep2 import RosdepDatabase
from scipy.spatial.transform import Rotation
import pcl.pcl_visualization
from vine import transform

num_of_points = 100000


def readXYZfile(filename, Separator=" "):
  data = []
  
  f = open(filename,'r') 
  line = f.readline() 
  num = 0
  while line:  #按行读入点云

     x,y,z = line.split(Separator)[:3]
     data.append([float(x),float(y),float(z)])  #X坐标
     num = num + 1
     line = f.readline()
  f.close() 
  

  return data

def get_rotationMatrix_from_euler(euler_list, pattern='XYZ', ret_np=False):
    rot = Rotation.from_euler(pattern, euler_list).as_matrix()
    if ret_np:
        rot = np.array(rot, dtype=np.float)
    return rot

# PointCloud Coordination Transform
def transfromCP(points, transf, ret_np=False):

    rotation = np.array(transf[:3,:3], dtype=np.float32)
    translation = np.array([transf[0][3],transf[1][3], transf[2][3]], dtype=np.float32)

    print("rotation: ", rotation)
    print("translation: ", translation)
    new_points = []
    
    for point in points:
        np.resize(point,(3,1))
        new_points.append(np.matmul(rotation, point) + translation)
    
    if ret_np:
        new_points = np.array(new_points, dtype=np.float32)
    
    return new_points

# Rotate PointCloud
def rotate_pointCloud(points, rot, ret_np=False):
    new_points = []
    
    for point in points:
        np.resize(point,(3,1))
        new_points.append(np.matmul(rot, point))
    
    if ret_np:
        new_points = np.array(new_points, dtype=np.float32)
    
    return new_points
    
def read_and_alig():
    path_1 = "/home/msi/1008_catkin_ws/src/realsenseD455_bridge/bunny/data/bun000.xyz"
    path_2 = "/home/msi/1008_catkin_ws/src/realsenseD455_bridge/bunny/data/bun045.xyz"
    cloud_in = pcl.PointCloud()
    cloud_out = pcl.PointCloud()
    
    points_1 = np.array(readXYZfile(path_1), dtype=np.float32)
    points_2 = np.array(readXYZfile(path_2), dtype=np.float32)
    
    cloud_in.from_array(points_1)
    cloud_out.from_array(points_2)
    
    # Rotate Only
    rot = get_rotationMatrix_from_euler([0,3.1415926/4,0], ret_np=True)
    rot_points_2 = rotate_pointCloud(points_2, rot, ret_np=True)
    rot_cloud_out = pcl.PointCloud()
    rot_cloud_out.from_array(rot_points_2)
    
    # Final = icp.align()
    
    icp = cloud_in.make_IterativeClosestPoint()
    converged, transf, estimate, fitness = icp.icp(cloud_in, cloud_out)
    print("fitness: ",fitness)
    # Transfrom
    new_points_2 = transfromCP(points_1, transf, ret_np=True)
    new_cloud_out = pcl.PointCloud()
    new_cloud_out.from_array(new_points_2)
    # cloud_out = new_cloud_out
        
    # color_cloud = pcl.PointCloud_PointXYZRGB(ego_pandar_points)
    
    vs=pcl.pcl_visualization.PCLVisualizering
    vss1 = pcl.pcl_visualization.PCLVisualizering()
    # visual.ShowColorCloud(color_cloud,b'cloud')
    visualcolor0 = pcl.pcl_visualization.PointCloudColorHandleringCustom(cloud_in, 250, 0, 0)# 设置颜色
    vs.AddPointCloud_ColorHandler(vss1,cloud_in,visualcolor0,id=b'cloud0',viewport=0)# 添加点云及标签
    
    visualcolor1 = pcl.pcl_visualization.PointCloudColorHandleringCustom(cloud_out, 0, 250, 0)# 设置颜色
    vs.AddPointCloud_ColorHandler(vss1,cloud_out,visualcolor1,id=b'cloud1',viewport=0)# 添加点云及标签
        
    visualcolor2 = pcl.pcl_visualization.PointCloudColorHandleringCustom(new_cloud_out, 0, 0, 200)# 设置颜色
    vs.AddPointCloud_ColorHandler(vss1,new_cloud_out,visualcolor2,id=b'cloud2',viewport=0)# 添加点云及标签
    
    visualcolor3 = pcl.pcl_visualization.PointCloudColorHandleringCustom(rot_cloud_out, 10, 200, 100)# 设置颜色
    vs.AddPointCloud_ColorHandler(vss1,rot_cloud_out,visualcolor3,id=b'cloud3',viewport=0)# 添加点云及标签
    while not vs.WasStopped(vss1):
        vs.Spin(vss1)

        
    
    
    
def main():
    cloud_in = pcl.PointCloud()
    cloud_out = pcl.PointCloud()

    # Fill in the CloudIn data
    # cloud_in->width    = 5;
    # cloud_in->height   = 1;
    # cloud_in->is_dense = false;
    # cloud_in->points.resize (cloud_in->width * cloud_in->height);
    # for (size_t i = 0; i < cloud_in->points.size (); ++i)
    # {
    #   cloud_in->points[i].x = 1024 * rand () / (RAND_MAX + 1.0f);
    #   cloud_in->points[i].y = 1024 * rand () / (RAND_MAX + 1.0f);
    #   cloud_in->points[i].z = 1024 * rand () / (RAND_MAX + 1.0f);
    # }
    points_in = np.zeros((num_of_points, 3), dtype=np.float32)
    RAND_MAX = 1024.0
    for i in range(0, num_of_points):
        points_in[i][0] = 1024 * random.random() / RAND_MAX
        points_in[i][1] = 1024 * random.random() / RAND_MAX
        points_in[i][2] = 1024 * random.random() / RAND_MAX

    cloud_in.from_array(points_in)

    # std::cout << "Saved " << cloud_in->points.size () << " data points to input:" << std::endl;
    # for (size_t i = 0; i < cloud_in->points.size (); ++i) std::cout << "    " <<
    #   cloud_in->points[i].x << " " << cloud_in->points[i].y << " " <<
    #   cloud_in->points[i].z << std::endl;
    # *cloud_out = *cloud_in;
    print('Saved ' + str(cloud_in.size) + ' data points to input:')
    points_out = np.zeros((num_of_points, 3), dtype=np.float32)

    # std::cout << "size:" << cloud_out->points.size() << std::endl;
    # for (size_t i = 0; i < cloud_in->points.size (); ++i)
    # cloud_out->points[i].x = cloud_in->points[i].x + 0.7f;

    # print('size:' + str(cloud_out.size))
    # for i in range(0, cloud_in.size):
    print('size:' + str(points_out.size))
    for i in range(0, cloud_in.size):
        points_out[i][0] = points_in[i][0] + 0.7
        points_out[i][1] = points_in[i][1]
        points_out[i][2] = points_in[i][2]

    cloud_out.from_array(points_out)

    # std::cout << "Transformed " << cloud_in->points.size () << " data points:" << std::endl;
    print('Transformed ' + str(cloud_in.size) + '\n data points:')

    # for (size_t i = 0; i < cloud_out->points.size (); ++i)
    #   std::cout << "    " << cloud_out->points[i].x << " " << cloud_out->points[i].y << " " << cloud_out->points[i].z << std::endl;
    # for i in range(0, cloud_out.size):
    #     print('     ' + str(cloud_out[i][0]) + ' ' + str(cloud_out[i]
    #                                                      [1]) + ' ' + str(cloud_out[i][2]) + '\n data points:')
    # for i in range(0, cloud_in.size):
    #     print('     ' + str(cloud_in[i][0]) + ' ' + str(cloud_in[i]
    #                                                      [1]) + ' ' + str(cloud_in[i][2]) + '\n data points:')
    # pcl::IterativeClosestPoint<pcl::PointXYZ, pcl::PointXYZ> icp;
    # icp.setInputCloud(cloud_in);
    # icp.setInputTarget(cloud_out);
    # pcl::PointCloud<pcl::PointXYZ> Final;
    # icp.align(Final);
    icp = cloud_in.make_IterativeClosestPoint()
    # Final = icp.align()
    converged, transf, estimate, fitness = icp.icp(cloud_in, cloud_out)

    # std::cout << "has converged:" << icp.hasConverged() << " score: " << icp.getFitnessScore() << std::endl;
    # std::cout << icp.getFinalTransformation() << std::endl;
    # print('has converged:' + str(icp.hasConverged()) + ' score: ' + str(icp.getFitnessScore()) )
    # print(str(icp.getFinalTransformation()))
    print('has converged:' + str(converged) + ' score: ' + str(fitness))
    print(str(transf))


if __name__ == "__main__":
    # import cProfile
    # cProfile.run('main()', sort='time')
    read_and_alig()