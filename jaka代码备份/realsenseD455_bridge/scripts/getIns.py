import pyrealsense2 as rs
import numpy as np
import cv2
import pcl

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.depth, 1280, 720, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 1280, 720, rs.format.bgr8, 30)

pipeline.start(config)

# 创建对齐对象（深度对齐颜色）
align = rs.align(rs.stream.color)

try:
    while True:
        frames = pipeline.wait_for_frames()

        # 获取对齐帧集
        aligned_frames = align.process(frames)

        # 获取对齐后的深度帧和彩色帧
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # 获取颜色帧内参
        color_profile = color_frame.get_profile()
        cvsprofile = rs.video_stream_profile(color_profile)
        color_intrin = cvsprofile.get_intrinsics()
        color_intrin_part = [color_intrin.ppx, color_intrin.ppy, color_intrin.fx, color_intrin.fy]
        print(color_intrin_part)
        # [318.48199462890625, 241.16720581054688, 616.5906372070312, 616.7650146484375]

        if not aligned_depth_frame or not color_frame:
            continue


finally:
  pipeline.stop()


'''
def my_depth_to_cloud():
    pc = rs.pointcloud()
    points = rs.points()
 
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
    config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
    pipe_profile = pipeline.start(config)
 
    for i in range(100):
        data = pipeline.wait_for_frames()
 
        depth = data.get_depth_frame()
        color = data.get_color_frame()
 
    frames = pipeline.wait_for_frames()
    depth = frames.get_depth_frame()
    color = frames.get_color_frame()
 
    colorful = np.asanyarray(color.get_data())
    colorful=colorful.reshape(-1,3)
 
    pc.map_to(color)
    points = pc.calculate(depth)
 
    #获取顶点坐标
    vtx = np.asanyarray(points.get_vertices())
    #获取纹理坐标
    #tex = np.asanyarray(points.get_texture_coordinates())
 
 
    with open('could.txt','w') as f:
        for i in range(len(vtx)):
            f.write(str(np.float(vtx[i][0])*1000)+' '+str(np.float(vtx[i][1])*1000)+' '+str(np.float(vtx[i][2])*1000)+' '+str(np.float(colorful[i][0]))+' '+str(np.float(colorful[i][1]))+' '+str(np.float(colorful[i][2]))+'\n')


def read():
    data = []
    with open('could.txt','r') as f:
        lines = f.readlines()
        num=0
        for line in lines:
            l=line.strip().split()
            data.append([np.float(l[0]),np.float(l[1]),np.float(l[2]),np.float(l[3]),np.float(l[4]),np.float(l[5])])
            #data.append([np.float(l[0]), np.float(l[1]), np.float(l[2])])
            num = num+1
 
 
    with open('cloud_rgb.txt', 'w') as f:
        for i in range(len(data)):
            f.write(str(np.float(data[i][0])) + ' ' + str(np.float(data[i][1])) + ' ' + str(np.float(data[i][2]))+ ' '  + str(np.int(data[i][3])<<16|np.int(data[i][4])<<8|np.int(data[i][5]))+'\n')   

def visual():
    cloud = pcl.PointCloud_PointXYZRGB()
    points = np.zeros((307200,4),dtype=np.float32)
 
    n=0
    with open('cloud_rgb.txt','r') as f:
        lines = f.readlines()
        for line in lines[:307100]:
            l=line.strip().split()
            #保存xyz时候扩大了1000倍，发现并没有用
            points[n][0] = np.float(l[0])/1000
            points[n][1] = np.float(l[1])/1000
            points[n][2] = np.float(l[2])/1000
            points[n][3] = np.int(l[3])
            n=n+1
 
    print(points[0:100]) #看看数据是怎么样的
    cloud.from_array(points) #从array构建点云的方式
 
    visual = pcl.pcl_visualization.CloudViewing()
    visual.ShowColorCloud(cloud)
 
    v = True
    while v:
        v = not (visual.WasStopped())    

     
my_depth_to_cloud()
'''



