#include <Servo.h>
#include <EEPROM.h>
//这个是左臂的程序 由于专用性的原因 已经不适配其余nano版
#define baudrate 115200  //定义通讯波特率  //这个目前是用美国黄金右手进行的测试 之后子机号要进行改变 这个是最后的版本
#define slaveID 4  //定义modbus RTU从站站号 左手对应1 左肩对应2 右肩对应3 右手 对应4
#define modbusDataSize 450  //定义modbus数据库空间大小,可根据实际情况自行修改大小
#define moveSize 75
#define servo_attach_num 8  //连接舵机数 部分nano没有连接全部6个舵机

unsigned int modbusData[modbusDataSize]={};   //建立modbus数据库
unsigned char movearea_min[8]={22,16,20,30,25,0,0,0};                //校准值较低值
unsigned char movearea_max[8]={122,135,153,150,135,0,0,0};                //校准值较高值
float hand_k[servo_attach_num];
float servo_angle[servo_attach_num];  //0拇指 1食指 2中指 3无名 4 小拇指 5 手腕

unsigned char keep_servo[8]={0,0,0,0,0,0,0,0};
unsigned char keep_servo_angle[8]={0,0,0,0,0,0,0,0};

unsigned char angle_now[2]={255,128};
//此处可以配置上电时即启用的舵机，舵机会保持在配置角度，用于提供基础支撑，如头部与腰部
Servo servos[servo_attach_num];
//系统参数
#define bufferSize 255  //一帧数据的最大字节数量
unsigned char frame[bufferSize];  //用于保存接收或发送的数据
HardwareSerial* ModbusPort;
//函数声明
unsigned int calculateCRC(unsigned char* _regs,unsigned char arraySize);  //声明CRC校验函数
void modbusRTU_slave();  //声明modbus RTU从站函数
void responseError(unsigned char ID,unsigned char function,unsigned char wrongNumber);  //声明错误信息返回函数
void modbusRTU_INI(HardwareSerial *SerialPort);  //声明modbus RTU端口初始化函数


void setup() 
{
    pinMode(LED_BUILTIN, OUTPUT);
    int eeAddress = 0;
    unsigned char error_flag=0;
    unsigned char min_flag=255;
    unsigned char max_flag=255;
    for(int clar=0;clar<modbusDataSize;clar++)  //缓存清零
    {
      modbusData[clar]=0;
    }
    //下列代码为校准范围正确的赋值
    EEPROM.get(0+18*sizeof(unsigned char), min_flag);  //2*8位之后 紧跟校准标志 如果曾进行过校准 此处将为1 否则为0xff 在未进行过校准时 使用程序开头的固定数组作为校准范围
    EEPROM.get(0+19*sizeof(unsigned char), max_flag);  //如果进行过校准 则使用eeprom内数组作为校准范围参考
    
        for(int i=0;i<8;i++)
        {
            EEPROM.get(eeAddress, movearea_min[i]);  //获取eeprom内的运动范围最小值数据
            eeAddress += sizeof(unsigned char);
        }
    
    
        for(int i=0;i<8;i++)
        {
            EEPROM.get(eeAddress, movearea_max[i]);  //获取eeprom内的运动范围最大值数据
            eeAddress += sizeof(unsigned char); 
        }
    
    for(int i=0;i<8;i++)   //在数据空间中留位置 待查询
    {
        modbusData[434+i]=movearea_min[i];
    }
    for(int i=0;i<8;i++)
    {
        modbusData[442+i]=movearea_max[i];
    }
//    for(int i=0;i<8;i++)   //未校准的电机 默认放缩系数为0或0xff 运动时仅保持中位
//    {
//        if(movearea_min[i]==0||movearea_min[i]==0xff)
//        {
//            movearea_min[i] = 90;
//        }  
//    }
//    for(int i=0;i<8;i++)
//    {
//        if(movearea_max[i]==0||movearea_max[i]==0xff)
//        {
//            movearea_max[i] = 90;
//        }  
//    }
//    for(int i=0;i<servo_attach_num;i++)   //数据检查 如果范围小值大于范围大值或范围小值为满值时为显著错误
//    {
//        if(movearea_min[i]>movearea_max[i]||movearea_min[i]==0xff)
//        {
//            error_flag=1;
//        }
//    }
//    if(error_flag == 1)    //显著错误时使用默认值
//    {
//        movearea_min[0]=22;
//        movearea_min[1]=16;
//        movearea_min[2]=20;
//        movearea_min[3]=30;
//        movearea_min[4]=25;
//        movearea_min[5]=60;
//        movearea_min[6]=60;
//        movearea_min[7]=60;
//        
//        
//        movearea_max[0]=122;
//        movearea_max[1]=135;
//        movearea_max[2]=153;
//        movearea_max[3]=150;
//        movearea_max[4]=135;
//        movearea_max[5]=120;      
//        movearea_max[6]=120;
//        movearea_max[7]=120;
//    }
    //计算校准系数
    for(int i=0;i<servo_attach_num;i++)
    {
        hand_k[i]=(movearea_max[i]-movearea_min[i])/254.0;
    }
  
    delay(100);
    modbusRTU_INI(&Serial);  //定义modbus通讯端口 端口0:&Serial 端口1:&Serial1 端口2:&Serial2
    modbusData[0]=0;         //默认初始模式停止
    modbusData[1]=128;        //默认初始位置归中
    modbusData[2]=128;
    modbusData[3]=128;
    modbusData[4]=128;
    modbusData[5]=128;
    modbusData[6]=128;
    modbusData[7]=128;
    modbusData[8]=128;
}

void loop() {
    unsigned char angle_check = 90; //默认校准初值
    modbusRTU_slave();  //执行modbus函数
    if(modbusData[0]==1)  //在线仿真模式
    {
        digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
        for(int j=0;j<8;j++)        //驱动手指5关节舵机
        {
            if(modbusData[j+1]!=0)
            {
                servos[j].attach(6+j);
                servo_angle[j]=modbusData[j+1];
                servo_angle[j] = (servo_angle[j]-1)*hand_k[j]+movearea_min[j];
                servos[j].write(servo_angle[j]);
            }
        }
        /*for(int j=0;j<3;j++)
        {
              
        }*/
        /*for(int j=6;j<8;j++)    //臂的两个舵机
        {
        if(modbusData[j+1]!=0)
            {
                servos[j].attach(5+j);
                servo_angle[j]=modbusData[j+1];
                servo_angle[j] = (servo_angle[j-1])*hand_k[j]+movearea_min[j];
                servos[j].write(servo_angle[j]);
            }
            if(modbusData[j+1]!=0)
            {
                servos[j].attach(5+j);
                servo_angle[j]=modbusData[j+1];
                servo_angle[j] = (servo_angle[j-1])*hand_k[j]+movearea_min[j];
                servos[j].write(servo_angle[j]);
            }
        }
        */
        /*for(int j=2;j<6;j++)    //第3,4,5,6位舵机直接计算赋值（对应头部左右上下嘴巴眼球）
        {
            if(modbusData[j+1]!=0)
            {
            servos[j].attach(6+j);
            servo_angle[j]=modbusData[j+1];
            servo_angle[j]=(servo_angle[j]-1)*hand_k[j]+movearea_min[j];
            servos[j].write(servo_angle[j]);
            }
        }
        
        }*/
    }
    else if (modbusData[0]==2)  //动作编排模式启动
    {
        unsigned long time_later = millis();//获取运动编排执行瞬间系统时间值
        unsigned char ii=0;
        //modbus数据库从地址0x000f开始为时间位 可以存放movesize位时间
        for (ii=0;ii<moveSize;ii++)
        {
            if(modbusData[0x000f+ii]==0 && modbusData[0x000f+ii+1]==0 && modbusData[0x000f+ii+2]==0 && modbusData[0x000f+ii+3]==0) //若读到时间数据连续为零 表示编排运动执行完成 跳出循环
            {
                break;
            }
            else if (modbusData[0x000f+ii]<=modbusData[0x000f+ii-1]&& !(modbusData[0x000f+ii]==0 && modbusData[0x000f+ii+1]==0&& modbusData[0x000f+ii+2]==0) )
            {
                //此时应该续秒
                
                for(int delay_time=0;delay_time<((modbusData[0x000f+ii-1]-modbusData[0x000f+ii-2])/100) ;delay_time++)
                {
                    //modbusRTU_slave();
                    delay(100);
                }
                time_later = millis();
            }
            while( (millis()-time_later) < modbusData[0x000f+ii] )//是否达到指定时间 未达到时等待 0       0 2000 5000 7000 0 2000 0 0 0 0 
            {   
                //modbusRTU_slave();  //执行modbus函数 等待时保持监听接口
            }
            //获取舵机位置数据
            servo_angle[0]=modbusData[0x0064+4*ii]>>8;
            servo_angle[1]=modbusData[0x0064+4*ii]&0x00ff;
            servo_angle[2]=modbusData[0x0065+4*ii]>>8;
            servo_angle[3]=modbusData[0x0065+4*ii]&0x00ff;
            servo_angle[4]=modbusData[0x0066+4*ii]>>8;
            servo_angle[5]=modbusData[0x0066+4*ii]&0x00ff;
            servo_angle[5]=modbusData[0x0067+4*ii]>>8;
            servo_angle[5]=modbusData[0x0067+4*ii]&0x00ff;
            //舵机驱动 带比例系数 获取数据为1-255之间 0为保持原响应 转换后舵机角度值在movearea min-max之间
            for(int j=0;j<servo_attach_num;j++)
            {
                if(servo_angle[j]==0)  //第j+1个舵机 数据为0时保持
                {}
                else
                {
                    servos[j].attach(6+j);
                    servo_angle[j]=(servo_angle[j]-1)*hand_k[j]+movearea_min[j];
                    servos[j].write(servo_angle[j]);
                }
            }
        }
        //全部动作执行完成 锁定舵机 恢复模式至模式0 
        for(int i = 0;i<200;i++)
        {
            delay(10);
            //modbusRTU_slave();
        }
        //等待动作完成
        modbusData[0]=0;
        for(int j=0;j<servo_attach_num;j++)
        {
            servos[j].detach();
        }
    }
    else if(modbusData[0]==3)      //校准模式
    {
        modbusRTU_slave();  //执行modbus函数
        if(modbusData[9]==0)  //校准舵机指示位  第10位指定校准舵机编号 1- servo_attach_num 第11位校准控制字符 3回归中位 1 确认最小值 2确认最大值 其余为正常校准模式 第12位校准方向 第13位校准增减启动位
        {}
        else
        {
            if(modbusData[9]>=1&&modbusData[9]<=8) //符合舵机编号范围
            {
                unsigned char servo_later = modbusData[9];
                unsigned char servo_true_num = modbusData[9]-1;
                while(modbusData[0]==3)
                {
                    modbusRTU_slave();  //执行modbus函数
                    if(modbusData[10]==3)   //控制指令段
                    {
                        angle_check = 90;  //回归中位
                        modbusData[10]=0;
                    }
                    else if(modbusData[10]==1)  //当前角度为对应舵机最小值
                    {
                        movearea_min[modbusData[9]-1]=angle_check;
                        EEPROM.put((modbusData[9]-1)*sizeof(unsigned char),angle_check);//存储
                        EEPROM.put(18*sizeof(unsigned char),1);//最小值校准标记
                        angle_check =90;
                        modbusData[10]=0;
                    }
                    else if(modbusData[10]==2) //当前角度为最大值
                    {
                        movearea_max[modbusData[9]-1]=angle_check;
                        EEPROM.put((modbusData[9]+7)*sizeof(unsigned char),angle_check);//存储
                        EEPROM.put(19*sizeof(unsigned char),1);//最大值校准标记
                        angle_check=90;
                        modbusData[10]=0;
                    }
                    else
                    {
                      
                    }
                    if(modbusData[11]==1&&modbusData[12]!=0)    //校准角度增减 1增 2减
                    {
                        angle_check = angle_check +modbusData[12];
                        if(angle_check>=180)
                        {
                            angle_check=90;  
                        }
                        modbusData[12]=0;
                    }
                    else if(modbusData[11]==2 && modbusData[12]!=0)
                    {
                        if(angle_check>modbusData[12])
                        {
                            angle_check = angle_check -modbusData[12];
                        }
                        else
                        {
                            angle_check = 90;
                        }
                        modbusData[12]=0;
                    }
                    if(modbusData[9]>=1&&modbusData[9]<=8)
                    {
                        servos[servo_true_num].attach(modbusData[9]+5);
                        servos[servo_true_num].write(angle_check);
                    }
                }
                //EEPROM.put(0+17*sizeof(unsigned char),0x01);//存储校准标志
                //EEPROM.put(0+18*sizeof(unsigned char),0x01);//存储校准标志  此处可以优化 变得一一对应
            }
        }
    }
    else if (modbusData[0]==4)   //清零缓存 准备新动作
    {
        for(int i = 0x000f ; i<388;i++)
        {
            modbusData[i]=0;  
        }
        modbusData[0]=0;
    }
    else //模式0 全舵机断电 停止待机模式
    {
        digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
        for(int j=0;j<8;j++)
        {
            if(keep_servo[j]==0)
            {
            servos[j].detach();
            }
            else
            { 
                servos[j].attach(6+j);
                servos[j].write((keep_servo_angle[j]-1)*hand_k[j]+movearea_min[j]);
            }
        }
    }
}


//modbus RTU端口初始化函数
//参数:端口号
void modbusRTU_INI(HardwareSerial *SerialPort)
{
  ModbusPort = SerialPort;
  (*ModbusPort).begin(baudrate);
  (*ModbusPort).flush();  
}

//modbus RTU从站函数
//支持功能码03,06,16
void modbusRTU_slave()
{
  unsigned int characterTime; //字符时间
  unsigned char errorFlag=0;  //错误标志
  unsigned int crc16;  //校验位
  unsigned char address=0;

  if (baudrate > 19200)  //波特率大于19200时进入条件
  {
    characterTime = 750; 
  }
  else
  {
    characterTime = 15000000/baudrate;  //1.5字符时间
  }
  while((*ModbusPort).available()>0)  //如果串口缓冲区数据量大于0进入条件
  {
    
    if(address<bufferSize)  //接收的数据量应小于一帧数据的最大字节数量
    {
      frame[address]=(*ModbusPort).read();
      address++;
    }
    else  //条件不满足时直接清空缓冲区
    {
       (*ModbusPort).read();
    }
    delayMicroseconds(characterTime);  //等待1.5个字符时间
    if((*ModbusPort).available()==0)  //1.5个字符时间后缓冲区仍然没有收到数据,认为一帧数据已经接收完成,进入条件
    {
      unsigned char function=frame[1];  //读取功能码      
      if(frame[0]==slaveID||frame[0]==0)  //站号匹配或者消息为广播形式,进入条件
      {
        crc16 = ((frame[address - 2] << 8) | frame[address - 1]);
        if(calculateCRC(&frame[0],address - 2)==crc16)  //数据校验通过,进入条件
        {
          if (frame[0]!=0 && (function == 3))  //功能码03不支持广播消息
          {
            unsigned int startData=((frame[2] << 8) | frame[3]);  //读取modbus数据库起始地址           
            unsigned int dataSize=((frame[4] << 8) | frame[5]);  //需要读取的modbus数据库数据长度
            unsigned int endData=startData+dataSize;    //需要读取的modbus数据库数据的结束地址
            unsigned char responseSize=5+dataSize*2;  //计算应答的数据长度
            unsigned int temp1,temp2,temp3;
            
            if(dataSize>125 || endData>modbusDataSize)  //读取数据的结束地址超过了modbus数据库的范围或单次读取的数据数量大于125
            {
              errorFlag=0x02;  //数据超过范围
              responseError(slaveID,function,errorFlag);  //返回错误消息
            }
            else
            {
              frame[0]=slaveID;  //设定站号
              frame[1]=function;  //设定功能码
              frame[2]=dataSize*2;  //设定数据长度
              temp3=3;
              for(temp1=startData;temp1<endData;temp1++)
              {
                temp2=modbusData[temp1];  //取出modbus数据库中的数据
                frame[temp3]=temp2>>8;
                temp3++;
                frame[temp3]=temp2 & 0xFF;
                temp3++;
              }
              crc16 = calculateCRC(&frame[0],responseSize-2);
              frame[responseSize-2] = crc16 >> 8;  //填写校验位
              frame[responseSize-1] = crc16 & 0xFF;
              (*ModbusPort).write(&frame[0],responseSize);  //返回功能码03的消息
            }
          }
          else if(function == 6)  //功能码为06时进入条件
          {
            unsigned int startData=((frame[2] << 8) | frame[3]);  //写入modbus数据库的地址           
            unsigned int setData=((frame[4] << 8) | frame[5]);  //写入modbus数据库的数值
            if(startData>modbusDataSize)
            {
              errorFlag=0x02;  //数据超过范围
              responseError(slaveID,function,errorFlag);  //返回错误消息
            }
            else
            {
              modbusData[startData]=setData;  //写入数据到modbus数据库              
              frame[0]=slaveID;  //设定站号
              frame[1]=function;  //设定功能码
              frame[2] = startData >> 8;  //填写数据库地址
              frame[3] = startData & 0xFF;             
              frame[4] = modbusData[startData] >> 8;  //填写数据库数值
              frame[5] = modbusData[startData] & 0xFF;
              crc16 = calculateCRC(&frame[0],6);  //计算校验值
              frame[6] = crc16 >> 8;  //填写校验位
              frame[7] = crc16 & 0xFF;
              (*ModbusPort).write(&frame[0],8);  //返回功能码06的消息              
            }
          }
          else if(function == 16)  //功能码为16时进入条件
          {
            if(frame[6]!=address-9)  //校验数据长度
            {
              errorFlag=0x03;  //数据长度不符
              responseError(slaveID,function,errorFlag);  //返回错误消息
            }
            else  //校验数据长度正确
            {
              unsigned int startData=((frame[2] << 8) | frame[3]);  //写入modbus数据库起始地址           
              unsigned int dataSize=((frame[4] << 8) | frame[5]);  //需要写入的modbus数据库数据长度
              unsigned int endData=startData+dataSize;    //需要写入的modbus数据库数据的结束地址
              if(dataSize>125 || endData>modbusDataSize)  //读取数据的结束地址超过了modbus数据库的范围或单次读取的数据数量大于125
              {
                errorFlag=0x02;  //数据超过范围
                responseError(slaveID,function,errorFlag);  //返回错误消息
              }
              else
              {              
                unsigned int temp1,temp2;
                temp2 = 7;  //从数据贞的第8个数据开始读取            
                for(temp1=startData;temp1<endData;temp1++)
                {
                  modbusData[temp1]=(frame[temp2]<<8|frame[temp2+1]);  //将数据写入modbus数据库中
                  temp2+=2;
                }
                frame[0]=slaveID;  //填写站号,frame[1]到frame[5]不变
                crc16 = calculateCRC(&frame[0],6);  //计算CRC校验
                frame[6] = crc16 >> 8;  //填写校验位
                frame[7] = crc16 & 0xFF;
                (*ModbusPort).write(&frame[0],8);  //发送功能码16的应答数据    
              }    
            }
          } 
          else  //其他功能码
          {
            errorFlag = 0x01;  //不支持收到的功能码
            responseError(slaveID,function,errorFlag);  //返回错误消息
          }      
        }
        else //数据校验错误
        {
          errorFlag = 0x04;
          responseError(slaveID,function,errorFlag);  //返回错误消息
        }
      }
    }
  }
}



//错误信息返回函数
//参数1:子机站号
//参数2:错误功能码
//参数3：错误反馈码
//无返回值，函数功能为按照485协议在通讯错误时反馈相应的错误信息
void responseError(unsigned char ID,unsigned char function,unsigned char wrongNumber)  //错误信息返回函数
{
  unsigned int crc16;  //校验位  
  frame[0] = ID;  //设定站号
  frame[1] = function+0x80;
  frame[2] = wrongNumber;  //填写错误代码
  crc16 = calculateCRC(&frame[0],3);  //计算校验值
  frame[3] = crc16 >> 8;  //填写校验位
  frame[4] = crc16 & 0xFF;
  (*ModbusPort).write(&frame[0],5);  //返回错误代码         
}

//CRC校验函数
//参数1:待校验数组的起始地址
//参数2:待校验数组的长度
//返回值CRC校验结果,16位,低字节在前
unsigned int calculateCRC(unsigned char* _regs,unsigned char arraySize) 
{
  unsigned int temp, temp2, flag;
  temp = 0xFFFF;
  for (unsigned char i = 0; i < arraySize; i++)
  {
    temp = temp ^ *(_regs+i);
    for (unsigned char j = 1; j <= 8; j++)
    {
      flag = temp & 0x0001;
      temp >>= 1;
      if (flag)
        temp ^= 0xA001;
    }
  }
  temp2 = temp >> 8;
  temp = (temp << 8) | temp2;
  temp &= 0xFFFF; 
  return temp; 
}



