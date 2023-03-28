#include <ModbusMaster.h>
#include <SPI.h>
#include <SD.h>

unsigned int calculateCRC(unsigned char* _regs,unsigned char arraySize);  //声明CRC校验函数
void refreshFile(unsigned char move_number);//文件清空函数
void refreshFile(String file_name);         //函数重载 字符串文件名的文件清空函数
void arraycalculate(unsigned char* _frame,unsigned char start_num);       //映射数组数据处理

#define bufferSize 255  //一帧数据的最大字节数量
#define baudrate 115200  //定义通讯波特率
//#define moveSize 100//定义最大运动编码指针范围
//#define servo_maxnum 32
//#define action_num_max 15

const int chipSelect = 53;
unsigned char frame[bufferSize];  //用于 数据
unsigned char code_number;        //用于计算收到的指令字节数目 进行指令集分类
//unsigned char move_address=0;//不同动作编码指针 在注销动作时归零 动作暂定最大为75个子动作 指针地址最大暂为255
//unsigned int  time_data[moveSize]={0};//对应2个动作 每动作对应最多75个时间戳 单位ms
//unsigned char move_data[moveSize*servo_maxnum]={0};//对应2个动作 每动作对应记录最多75组 X N 个舵机位置信息 舵机信息1-6 对应子机1 7-12对应子机2 13-18对应子机3 19-24对应子机4 超出暂不对应待优化
// instantiate ModbusMaster object
ModbusMaster node;
void setup() {
    Serial.begin(115200);
    Serial1.begin(115200);
    while (!Serial) 
    {
    }
    Serial.print("Initializing SD card...");
    if (!SD.begin(chipSelect)) 
    {
        Serial.println("Card failed, or not present");
        return;
    }
    Serial.println("card initialized.");  //打开两个串口 初始化SD
}

void loop() {
    File dataFile;
    unsigned int characterTime; //字符时间
    unsigned char address=0;
    uint8_t result;
//    uint16_t data[6];
//    int i = 0;
//    int b = 0;
//    int password = 0;
    while(1)
    {    
        characterTime = 750; 
        while((Serial.available()>0))  //如果主串口缓冲区数据量大于0进入条件
        {
            if(address<bufferSize)  //接收的数据量应小于一帧数据的最大字节数量
            {
                frame[address]=Serial.read();
                address++;
            }
            else  //条件不满足时直接清空缓冲区
            {
                Serial.read();
                Serial.print("out of range");
            }
            delayMicroseconds(characterTime);  //等待1.5个字符时间
            if(Serial.available()==0)  //1.5个字符时间后缓冲区仍然没有收到数据,认为一帧数据已经接收完成,进入条件
            {
                code_number = address;
                address = 0;
                Serial.print("code_number=");
                Serial.println(code_number);
                if(code_number == 10)  // 8字节指令集 code 0 停止指定子机运动 code 1 启动指定子机运动至在线仿真姿态 code 3 获取指定子机在线仿真舵机状态角
                {
                    unsigned char To_slave = frame[0];
                    unsigned char code = frame[1];     //命令位 0舵机停止 1舵机启动  3读寄存器打印  7 锁定
                    node.begin(To_slave, Serial1);
                    if(code == 0)  //code 0 停止指定子机运动
                    {
                        result = node.writeSingleRegister(0x0000,0x00); //停止
                        if(result == node.ku8MBSuccess)
                        {
                            Serial.print("stop success");
                        }
                        else 
                        {
                            Serial.print("error:stop");
                            Serial.print(result);
                        }
                        
                    }
                    else if(code == 1)   //code 1 启动指定子机运动至在线仿真姿态 
                    {
                        for(unsigned char t=0;t<8;t++)
                        {
                            node.setTransmitBuffer(t,frame[t+2]);
                            
                        }
                        result = node.writeMultipleRegisters(0x0001,0x08);
                        if(result == node.ku8MBSuccess)
                        {
                            result = node.writeSingleRegister(0x0000,0x01); //启动
                            if(result == node.ku8MBSuccess)
                            {
                                Serial.print("start success");
                            }
                            else 
                            {
                                Serial.print("error:start");
                                Serial.print(result);
                            }
                        }
                        else 
                        {
                            Serial.print("error start:multi");
                            Serial.print(result);
                        }
                    }
                    else if(code == 3)    //读取子机信息
                    {
                        result = node.readHoldingRegisters(0x0000, 9);    //读9位
                        if(result == node.ku8MBSuccess)
                        {
                            Serial.println("read success");
                            Serial.println("servo angle");
                            Serial.println(node.getResponseBuffer(0x00));      //打印模式标志位
                            for(unsigned char i=0;i<8;i++)
                            {
                                Serial.println(node.getResponseBuffer(i+1));   //打印子机第1-8位  8位舵机当前角度
                            }
                            result = node.readHoldingRegisters(434, 16);        //读取打印舵机校准范围
                            if(result == node.ku8MBSuccess)
                            {
                                Serial.println("area data min");
                                for(unsigned char i=0;i<8;i++)
                                {
                                    Serial.println(node.getResponseBuffer(i));
                                }
                                Serial.println("area data max");
                                for(unsigned char i=0;i<8;i++)
                                {
                                    Serial.println(node.getResponseBuffer(i+8));
                                }                               
                            }
                            else 
                            {
                                Serial.print("error:read");
                                Serial.print(result);
                            } 
                        } 
                    }
                    else 
                    {
                        Serial.print("error:code");
                    }    
                }
                else if(code_number == 4)   //校准指令
                {
                     if(frame[3]==0&&frame[2]==0)   //末两位为0 
                    {
                        if(frame[0]>=1&&frame[0]<=32)  //校准舵机存在
                        {
                            unsigned char slave_check;
                            if(frame[0]<=8)                     //判断舵机所处子机
                            {slave_check=1;}
                            else if(frame[0]<=16)
                            {slave_check=2;}
                            else if(frame[0]<=24)
                            {slave_check=3;}
                            else if(frame[0]<=32)
                            {slave_check=4;}
                            unsigned char check_servo_position;
                            check_servo_position=frame[0]+8-slave_check*8;  //判断舵机位置
                            node.begin(slave_check, Serial1);//选定目标子机
                            result = node.writeSingleRegister(0x0000,3); //启动校准
                            if(result == node.ku8MBSuccess)
                            {
                                Serial.println("check servo...");
                                Serial.print("slave:");
                                Serial.print(slave_check);
                                Serial.print("servo:");
                                Serial.println(check_servo_position);
                                result = node.writeSingleRegister(0x0009,check_servo_position);    //校准舵机编号写在9号位
                                if(result == node.ku8MBSuccess)
                                {
                                    if(frame[1]==128)//归中  0x80
                                    {
                                        result = node.writeSingleRegister(0x000a,3);   //对于子机数据库第10位置3  子机驱动该舵机回到中位
                                        if(result == node.ku8MBSuccess)
                                        {
                                            Serial.println("return medium success"); 
                                        }
                                        else 
                                        {
                                            Serial.print("error:check");
                                            Serial.println("return medium"); 
                                        }
                                    }
                                    else if(frame[1]==1)//记为最小值
                                    {
                                        result = node.writeSingleRegister(0x000a,1); 
                                        if(result == node.ku8MBSuccess)
                                        {
                                            Serial.println("set minmum success");
                                        }
                                        else 
                                        {
                                            Serial.print("error:check");
                                            Serial.println("minmum"); 
                                        }
                                    }
                                    else if(frame[1]==255)//记为最大值
                                    {
                                        result = node.writeSingleRegister(0x000a,2); 
                                        if(result == node.ku8MBSuccess)
                                        {
                                            Serial.println("set maxmum success");
                                        }
                                        else 
                                        {
                                            Serial.print("error:check");
                                            Serial.println("maxmum"); 
                                        }
                                    }
                                    else if(frame[1]==0) //脱离校准
                                    {
                                        result = node.writeSingleRegister(9,0);
                                        if(result == node.ku8MBSuccess)
                                        {
                                            result = node.writeSingleRegister(0,0);
                                            if(result == node.ku8MBSuccess)
                                            {
                                                Serial.println("break check success");
                                            }
                                            else
                                            {
                                                Serial.println("break check failed");  
                                            }
                                        }
                                        else
                                        {
                                            Serial.println("clear check num failed");
                                        }
                                    }
                                    else if(frame[1]>=98&&frame[1]<=158)//最大每次校准范围在30度内 防止过激
                                    {
                                        if(frame[1]>=98&&frame[1]<128) //调小   //输入比0x80小的时候  认为是要将舵机输出调小
                                        {
                                            result = node.writeSingleRegister(11,2);   //对于第11位 置2
                                            if(result == node.ku8MBSuccess)
                                            {
                                                result = node.writeSingleRegister(12,128-frame[1]);
                                                if(result == node.ku8MBSuccess)
                                                {
                                                    Serial.println("go small success");
                                                }
                                                else
                                                {
                                                    Serial.print("error:check");
                                                    Serial.println("go small");
                                                }
                                            }
                                            else 
                                            {
                                                Serial.print("error:check");
                                                Serial.println("go "); 
                                            }
                                        }
                                        else                          //调大
                                        {
                                            result = node.writeSingleRegister(11,1);
                                            if(result == node.ku8MBSuccess)
                                            {
                                                result = node.writeSingleRegister(12,frame[1]-128);
                                                if(result == node.ku8MBSuccess)
                                                {
                                                    Serial.println("go big success");
                                                }
                                                else
                                                {
                                                    Serial.print("error:check");
                                                    Serial.println("go big");
                                                }
                                            }
                                            else 
                                            {
                                                Serial.print("error:check");
                                                Serial.println("go"); 
                                            }
                                        }
                                    }
                                    else
                                    {
                                        Serial.println("check angle out of range");
                                    }
                                }
                                else
                                {
                                    Serial.print("error:check");
                                    Serial.print("check position");
                                }
                            }
                            else 
                            {
                                Serial.print("error:check");
                                Serial.print("start");
                            }  
                        }
                        else
                        {
                            Serial.println("error:check num");
                        }
                    }
                    else
                    {
                        Serial.println("error:check");
                    }
                }
                else if(code_number==29 && frame[0]==0xff && frame[1]==0xff ) //全关节映射
                {
                    Serial.print("joints mapping");
                    unsigned int  crc16 = ((frame[27] << 8) | frame[28]);
                    unsigned char mapping_data[25];  //全关节映射中共有25个数据位
                    for(int k=0;k<25;k++)            //映射舵机赋值
                    {
                        mapping_data[k]=frame[2+k];//映射角度数据数组
                    }
                    if(calculateCRC(&frame[0],27)==crc16)  //数据校验通过,进入条件
                    {
                        unsigned char mapping_data_high;
                        unsigned char mapping_data_low;
                        unsigned int mapping_data_trans;
                        //arraycalculate(unsigned char* _frame,unsigned char start_num)；
                        node.begin(2, Serial1);
                        node.setTransmitBuffer(0,1);             //2号子机启动
                        
                        node.setTransmitBuffer(5,frame[16]);     //右臂侧展
                        node.setTransmitBuffer(6,frame[17]);     //右臂前后
                        //frame[12]=256-frame[12];
                        node.setTransmitBuffer(3,frame[12]);     //头部左右
                        frame[13]=256-frame[13];
                        node.setTransmitBuffer(4,frame[13]);     //头部上下
                        frame[10]=256-frame[10];
                        node.setTransmitBuffer(1,frame[10]);
                        frame[11]=256-frame[11];
                        node.setTransmitBuffer(2,frame[11]);    
                        result = node.writeMultipleRegisters(0x0000,0x09);   //映射数据写入
                        if(result == node.ku8MBSuccess)
                        {
                        }
                        else
                        {
                            Serial.println("first boom");           
                        }
                        delay(10);
                        node.begin(3, Serial1);  
                        frame[18]=256-frame[18];//对大拇指取反
                        for(int jj1 =0;jj1<5;jj1++ ) //对于右手的映射 从第19位开始-第24位的6位依次映射至拇指到手腕
                        {
                            node.setTransmitBuffer(jj1+1,frame[jj1+18]);
                        }
                        node.setTransmitBuffer(7,frame[14]);
                        frame[23]=256-frame[23];
                        node.setTransmitBuffer(6,frame[23]);
                        node.setTransmitBuffer(8,frame[15]);
                        node.setTransmitBuffer(0,1);
                        Serial.println("mid");
                       
                        result = node.writeMultipleRegisters(0x0000,0x09);   //映射数据写入
                        if(result == node.ku8MBSuccess)
                        {}
                        else
                        {
                            Serial.println("2st boom");  
                        }
                        
                        node.begin(1, Serial1);
                        
                        for(int jj1 =0;jj1<5;jj1++ ) //对于左手的映射 
                        {
                            frame[jj1+2]=256-frame[jj1+2];
                            node.setTransmitBuffer(jj1+1,frame[jj1+2]);
                        }
                        node.setTransmitBuffer(7,frame[8]);
                        node.setTransmitBuffer(6,frame[7]);
                        node.setTransmitBuffer(8,frame[9]);
                        
                        node.setTransmitBuffer(0,1);
                        Serial.println("mid");
                        delay(10);
                        result = node.writeMultipleRegisters(0x0000,0x09);   //映射数据写入   
                    }
                    else
                    {
                        Serial.print("error mapping crc");
                    }
                }
            }
        }
    }
}

//映射数据处理函数
//参数1：映射数据数组的起始地址
//参数2：映射子机启动位
//无返回值
void arraycalculate(unsigned char* _frame,unsigned char start_num)
{
    
  
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
//文件清空函数 
//输入值为数字 
//功能为清空对应数字编号的运动数据文件
//无返回值
void refreshFile(unsigned char move_number) 
{
    String file_name="";
    File file_current;    
    file_name = "action"+String(move_number)+".txt";
    if (SD.exists(file_name))          //判断动作文件是否存在
    {
        SD.remove(file_name);
    } 
    else 
    {}
    if (SD.exists(file_name))          //再次确认动作文件是否存在
    {
        SD.remove(file_name);
    } 
    else 
    {
        file_current = SD.open(file_name,FILE_WRITE);  //打开文件一次 再次关闭
        file_current.close();
    }
}
//文件清空函数 
//输入值为字符串 
//功能为清空对应数字编号的运动数据文件
//无返回值
void refreshFile(String file_name) 
{
    File file_current;    
    if (SD.exists(file_name))          //判断动作文件是否存在
    {
        SD.remove(file_name);
    } 
    else 
    {}
    if (SD.exists(file_name))          //再次确认动作文件是否存在
    {
        SD.remove(file_name);
    } 
    else 
    {
        file_current = SD.open(file_name,FILE_WRITE);  //打开文件一次 再次关闭
        file_current.close();
    }
}
