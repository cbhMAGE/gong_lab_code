# 1_Controller_pkg



## 📖 目录

- [📖 目录](#-目录)
- [📝 简介](#-简介)
- [💻 代码框架](#-代码框架)
- [⚙️ 硬件要求](#️-硬件要求)
- [🛠️ 环境配置](#️-环境配置)
- [🚀 快速开始](#-快速开始)
- [🤔 代码解读](#-代码解读)



## 📝 简介

本文档所提供的传感器数据获取和遥操作映射算法支持使用者穿戴Noitom公司的**Perception Neuron 3动作捕捉装置**获取传感器数据。同时提供了多种传感器数据使用样例，分别用于控制**JAKA机器人平台**和**INMOOV类人机器人平台**。开发者可以直接调用我们的框架来进行以上两款已适配机器人的遥操作控制，也可以通过解析获取的传感器数据，自行设计映射算法对新的采摘机器人机型进行遥操作控制。

为方便不熟悉的同学使用，我们将在后续详细介绍代码的框架，硬件和软件的环境配置，和提供当前样例的详细操作方法和视频教程。



## 💻 代码框架

本代码仓主要分为三个部分，分别为动捕部分，映射部分和控制部分。

![image-20241130205529198](./assets/image-20241130205529198.png)

- 动捕部分主要由Noitom公司的官方代码和API组成，用于获取动捕设备的传感器数据并进行解析。
- 映射部分由我组同学自行编写，目前存在三个版本：v1.0为徐文彬编写的INMOOV机器人映射算法；v2.0为黄威复杂机电组编写的JAKA机器人映射算法；v3.0为吴非凡编写的JAKA机器人映射算法。该部分代码用于将传感器数据解析并构建传感器数据-机器人控制量映射关系，获取机器人控制数据。
- 控制部分由我组同学自行编写，目前存在三个版本：v1.0为李旭东编写的INMOOV机器人控制算法；v2.0为杨志宇编写的JAKA机器人控制算法；v2.0-beta为黄威，吴非凡等在v2.0版基础上根据自己需求进行改写的测试版，未定型为工程使用版本。



本代码仓主要数据流如下所示。

![image-20241130210013752](./assets/image-20241130210013752.png)



## ⚙️ 硬件要求

- Perception Neuron 3动作捕捉设备([Noitom](https://shopcdn.noitom.com.cn/html/208.html))
- Windows10/11服务器，用于接收动捕设备数据
- Linux服务器，用于接收关节控制数据，并对机器人进行实时控制
- JAKA机器人(可选)
- INMOOV机器人(可选)



## 🛠️ 环境配置

**Windows服务器**

- Axis Studio，该软件为Noitom编写的传感器数据接收软件。

  - 配置方法：打开[网站](https://shop.noitom.com.cn/common/product_item/index.jhtml?productItemId=6)，下载后选择指定路径安装即可。

- MocapAPI，用于接收BVH数据广播信息，使得可以在代码层对数据进行解析映射的API接口。

  - 配置方法1：打开[网站](https://shop.noitom.com.cn/common/product_item/index.jhtml?productItemId=6)，下载后选择指定路径安装即可。**[批注/陈斌豪]：选择路径是否有要求？API代码是否有需要修改的地方？如端口等？**
  - 配置方法2：通过Github源代码进行安装，请运行以下命令：

  ```bat
  git clone https://github.com/pnmocap/MocapApi.git
  cd MocapApi
  install.bat
  ```

- TomatoHarvesterMocap，用于获取传感器数据并进行映射，通过socket下发给linux服务器。

  - 配置方法：通过Github或组内私有云下载源代码，请运行以下命令：

  ```bat
  git clone https://github.com/gongliang_robot/TomatoHarvesterMocap.git
  cd TomatoHarvesterMocap/x64/release
  ```

  启动EXE文件即可运行。



**Linux服务器**

- ROS，机器人操作系统。

  - 配置方法：打开[网站](https://wiki.ros.org/ROS/Installation)，根据当前Linux版本选择合适的ROS版本进行安装。根据需求进行ROS环境的配置。ROS相关知识文档可以根据以下[网站](http://www.autolabor.com.cn/book/ROSTutorials/)进行简单的学习。

- bprinter，终端表格打印软件。

  - 配置方法：通过Github下载源代码，请运行以下命令：

  ```bash
  cd ~/Opt  # 可随意
  git clone https://github.com/dattanchu/bprinter.git
  cd bprinter
  mkdir build && cd build
  cmake .. && make -j4
  sudo make install
  ```

- jaka GUI，jaka机器人控制器gui：

  - 配置方法：通过Github或组内私有云下载源代码，请运行以下命令：

  ```bash
  git clone https://github.com/gongliang_robot/qjaka_gui.git
  ```

  下载后，打开代码仓中的`CmakLists.txt`，找到第35行附近，修改`set(Jaka_DIR "/home/msi/Opt/jaka_sdk")`为`set(Jaka_DIR "your sdk path")`

- Robot_model，包含JAKA机器人的urdf和moveit配置案例，保存于本代码仓下的`robot_model.zip`文件中，解压到对应路径即可。以下是压缩包中的文件简要说明。

  - `Zu7/urdf/jaka_macro.xacro`：添加了macro `prefix`，用以区分左右机械臂；
  - `Zu7/urdf/jaka_dual.xacro`：双臂；
  - `Zu7/urdf/jaka.urdf.xacro`：官方文件，单机械臂；
  - `dual_moveit_config`：使用moveit配置助手，基于`Zu7/urdf/jaka_dual.xacro`生成的。

## 🚀 快速开始

本章节介绍基本使用，更丰富的使用和修改方式请详细查看[代码解读](#-代码解读)章节。



- 动捕设备与软件准备

  - 开启软件
    - 运行Axis Studio，选择Sample Project。
    - 点击右上方![img](./assets/clip_image002.jpg)图标，进入设置，选择“BVH数据广播”选项卡，对“BVH-广播”进行设置（该设置只需进行一次）。
    - 退出设置，进入上方“捕捉”栏。
  - 动捕设备开机
    - 通过长按红色按钮可以给单个传感器进行开/关操作，但充电仓断电会自动让其内的传感器开机，这样更为便捷。
    - 接收器需要通过USB连接至电脑。
    - 请确保传感器亮灯以及接收器亮灯颜色一致，这代表它们在同一频道。如果不一致，可以使用Axis Studio软件中的“频段设置”功能，或者双击传感器的按钮依次序更改频段。通常情况下，绿色频段与蓝色频段是信号强度最高的频段。
    - 使用完后，可以通过右侧![img](./assets/clip_image002-1732977667232-4.jpg)按钮关闭所有传感器。
  - 动捕设备连接
    - 点击右侧![img](./assets/clip_image002-1732977685728-6.jpg)按钮进行连接，此时可以穿戴也可以不穿戴。

- 穿戴动作捕捉设备与校准

  - 穿戴

    - 如果是进行单臂捕捉，则只需要腰部、背部、左肩、左大臂、左小臂、左手这6个传感器位点，按照下图穿戴。双臂以此类推。

    ![img](./assets/clip_image002-1732977706756-8.jpg)

  - 校准

    - 点击右侧![img](./assets/clip_image002-1732977724484-10.jpg)按钮并根据提示进行校准

- 运行遥操作程序

  - Linux服务器
    - 通过roslaunch运行pickingv2中的launch文件。
    - 在打开的gui界面中，启动机械臂并使能（根据需要取消勾选“仿真”选项框）
    - 点击“go”按钮
  - window服务器
    - 运行main.cpp编译生成的.exe文件，开始遥操作
  - 结束遥操作
    - 结束遥操作有两种方式：
      1. 在工控机的gui中点击“”按钮
      2. 上位机中时间达到限定值



## 🤔 代码解读

- 映射代码
  - main.cpp
    - 调用MocapApi
      - 准备工作，包括创建调用句柄以及设置接收BVH广播的IP和端口
      - **循环**读取各个关节的四元数数据
    - 校准。因为PN3的BVH数据以T-pose作为基准，当不使用T-pose作为基准的时候，需要设定一个矫正过程。
    - 映射，在**循环**内进行
      - 将四元数数据转化为旋转矩阵
      - 利用反三角函数从旋转矩阵中求解出机器人关节角
      - 对关节角进行限位以及限速
    - 使用TCP/IP协议将数据以double类型数组的形式发送
  - RotQua.cpp和RotQua.h
    - 定义Rotation类，用于将四元数转化为旋转矩阵
- 控制代码
  - QJAKA_GUI包，用途是控制机械臂的GUI，以下为重要代码文件：
    - mainwindow.cpp和.h
    - subwindow.cpp和.h，定义了subwindow类下的诸多成员函数
      - on_goBt_clicked函数
        - 在线程中运行
        - 设置socket用于接收关节角数据，且为非阻塞模式
        - 在一个缓冲区内存储目标关节角值，在循环中：
          - 当通过socket接收到新的目标关节角值时，填入缓冲区头部并运用差值算法填满整个缓冲区
          - 输出缓冲区尾部的目标关节角值用于机械臂控制
      - on_endSockBt_clicked函数
        - 断开socket连接
        - 使机械臂恢复到预设的初始值
      - 其他函数
    - subwindow.ui，定义了GUI的界面布局
  - pickingv2包
    - test_robot_task.launch，启动机械臂控制







