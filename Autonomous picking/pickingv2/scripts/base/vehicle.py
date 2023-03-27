import sys
import logging
import serial
import modbus_tk
import modbus_tk.utils
import modbus_tk.defines as cst
from modbus_tk import modbus_rtu
import time

# define 相对运动 和 绝对运动 标志
RELATIVE_MOTION = 0x0000
ABSOLUTE_MOTION = 0x0001


# 底盘控制类，实现基于modbus协议的底盘位置控制。
# 由于异常处理已经被写在 serial, modbus_tk 等库里，所以不必重写异常处理
# 变量和方法前的'_'代表私有成员，建议不直接使用
class Chassis():
    # 成员变量
    _connector = None  # modbus类
    _logger = modbus_tk.utils.create_logger("console")  # logger类

    # 构造函数
    def __init__(self, _port, _baudrate=19200, _bytesize=8, _parity='N', _stopbits=1) -> None:
        self._connector = modbus_rtu.RtuMaster(
            serial.Serial(port=_port, baudrate=_baudrate,
                          bytesize=_bytesize, parity=_parity, stopbits=_stopbits))
        self._connector.set_timeout(1.0)

    def close(self):
        self._connector.close()

    # public
    def moveByDistance(self, moveMode, value, MotorID=1):  # 相对或绝对运动
        # moveMode = 0x0000 相对运动模式
        # moveMode = 0x0001 绝对运动模式
        # 目前不知道这个Distance values的单位是什么
        rValues = [(value & 0xFFFF0000) >> 16, value & 0x0000FFFF]  # 分离高低16位
        lValues = [((-value) & 0xFFFF0000) >> 16, (-value) & 0x0000FFFF]

        self._setOperationMode(1 + MotorID, 0x0000)  # 设置操作模式：将操作模式（ 0x0024）设置成 "网络操作模式"
        self._setOperationMode(MotorID, 0x0000)

        self._setControlMode(1 + MotorID, 0x0002)
        self._setControlMode(MotorID, 0x0002)  # 设置控制模式：将控制模式（ 0x0025）设置成位置控制模式。

        self._setMoveMode(1 + MotorID, moveMode)
        self._setMoveMode(MotorID, moveMode)  # 设置运动模式：将运动模式（ 0x002D）设置成相对运动或者绝对运动(0-相对运行模式；1-绝对运行模式)。

        self._enableMotor(1 + MotorID, 0x0001)
        self._enableMotor(MotorID, 0x0001)  # 向地址 0x0028 中写入 1，电机使能，如写入 0 则释放电机使能

        self._setMoveingDistance(1 + MotorID, rValues)
        self._setMoveingDistance(MotorID, lValues)  # 写入一个 32 位有符号数，设定电机的运动距离。

        self._StartMove(1 + MotorID, 0x0001)
        self._StartMove(MotorID, 0x0001)  # 写入1，开始运动

    def isdistanceReached(self, MotorID):  # 判断距离是否达到设定值
        return self.getRealPosition(MotorID) == self.getSettedPosition(MotorID)

    # def moveBySpeed(self,MotorID,value):#相对或绝对运动
    #     # moveMode = 0x0000 相对运动模式
    #     # moveMode = 0x0001 绝对运动模式
    #     #目前不知道这个Distance values的单位是什么
    #     self._setOperationMode(MotorID,0x0000)     # 设置操作模式：将操作模式（ 0x0024）设置成 "网络操作模式"
    #     self._setControlMode(MotorID,0x0001)       # 设置控制模式：将控制模式（ 0x0025）设置成位置控制模式。
    #     self._setMovingSpeed(MotorID,value)        # 此速度设定值单位为 rmp“转/分钟”
    #     # self._enableMotor(deviceID,0x0001)          # 向地址 0x0028 中写入 1，电机使能，如写入 0 则释放电机使能

    def stopMoving(self, MotorID):
        self._StartMove(MotorID, 0x0000)  # 写入1，开始运动
        self._enableMotor(MotorID, 0x0000)
        self._StartMove(MotorID + 1, 0x0000)  # 写入1，开始运动
        self._enableMotor(MotorID + 1, 0x0000)  # 向地址 0x0028 中写入 1，电机使能，如写入 0 则释放电机使能

    def getRealPosition(self, MotorID):
        return self._read_MotorRealPos(MotorID)

    def getSettedPosition(self, MotorID):
        return self._read_MotorSettedPos(MotorID)

    def getMotorRealSpeed(self, MotorID):
        return self._read_MotorRealSpeed(MotorID)

    def getstatus(self, MotorID):
        return self._read_StatusMonitoring(MotorID)

    def wait_for_complete(self):
        while self.getSettedPosition(1) != self.getRealPosition(1):
            time.sleep(0.1)

    # private
    def _changeCoil(self, coilID, value, deviceID, ):
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_COIL, coilID, output_value=value))

    def _setOperationMode(self, deviceID, mode=0x0000):
        # mode = 0x0000 网络操作模式
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x0024, output_value=mode))

    def _setControlMode(self, deviceID, mode=0x0002):
        # mode = 0x0002 位置控制
        # mode = 0x0001 速度控制
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x0025, output_value=mode))

    def _setMoveMode(self, deviceID, mode=0x0000):
        # mode = 0x0000 相对运动模式
        # mode = 0x0001 绝对运动模式
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x002D, output_value=mode))

    def _enableMotor(self, deviceID, status=0x0000):
        # status = 0x0001 使能电机
        # status = 0x0000 释放电机
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x0028, output_value=status))

    def _setMoveingDistance(self, deviceID, values=(0, 0)):
        # 利用功能码 16 向地址 0x0026 写入一个 32 位有符号数，设定电机的运动距离。
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_MULTIPLE_REGISTERS, 0x0026, output_value=values))

    def _setMovingSpeed(self, deviceID, value=0):
        # 向 0x00AE 中写入速度值， 即可改变速度设定值，此速度设定值单位为 rmp“转/分钟”，
        # 如果是正值则是正转，反之则电机反转。

        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x00AE, output_value=value))

    def _StartMove(self, deviceID, status=0x0000):
        # status = 0x0001 开始运动
        self._logger.info(self._connector.execute(
            deviceID, cst.WRITE_SINGLE_REGISTER, 0x0029, output_value=status))

    def _read_MotorSettedPos(self, deviceID):
        return self._connector.execute(
            deviceID, cst.READ_HOLDING_REGISTERS, 0x00AA, 0x0002)

    def _read_MotorRealPos(self, deviceID):
        return self._connector.execute(
            deviceID, cst.READ_HOLDING_REGISTERS, 0x00AC, 0x0002)

    def _read_MotorRealSpeed(self, deviceID):
        return self._connector.execute(
            deviceID, cst.READ_HOLDING_REGISTERS, 0x00AF, 0x0001)

    def _read_StatusMonitoring(self, deviceID):
        return self._connector.execute(
            deviceID, cst.READ_HOLDING_REGISTERS, 0x00C8, 0x0002)


if __name__ == '__main__':
    c = Chassis('/dev/ttyUSB0')
    c.moveByDistance(0x0001, 10000, 1)
