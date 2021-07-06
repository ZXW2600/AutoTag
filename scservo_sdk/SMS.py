#!/usr/bin/env python

# 飞特舵机SMS舵机接口

import os

if os.name == 'nt':
    import msvcrt
    def getch():
        return msvcrt.getch().decode()
else:
    import sys, tty, termios
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    def getch():
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


from .port_handler import *
from .packet_handler import *
from .group_sync_read import *
from .group_sync_write import *

# Control table address
ADDR_SCS_TORQUE_ENABLE     = 40
ADDR_STS_GOAL_ACC          = 41
ADDR_STS_GOAL_POSITION     = 42
ADDR_STS_GOAL_SPEED        = 46
ADDR_STS_PRESENT_POSITION  = 56


# Default setting
SCS1_ID                     = 1                 # SCServo#1 ID : 1
SCS2_ID                     = 2                 # SCServo#1 ID : 2
BAUDRATE                    = 115200           # SCServo default baudrate : 1000000
DEVICENAME                  = '/dev/ttyUSB0'    # Check which port is being used on your controller
                                                # ex) Windows: "COM1"   Linux: "/dev/ttyUSB0" Mac: "/dev/tty.usbserial-*"

SCS_MINIMUM_POSITION_VALUE  = 100               # SCServo will rotate between this value
SCS_MAXIMUM_POSITION_VALUE  = 4000              # and this value (note that the SCServo would not move when the position value is out of movable range. Check e-manual about the range of the SCServo you use.)
SCS_MOVING_STATUS_THRESHOLD = 20                # SCServo moving status threshold
SCS_MOVING_SPEED            = 0                 # SCServo moving speed
SCS_MOVING_ACC              = 0                 # SCServo moving acc
protocol_end                = 0                 # SCServo bit end(STS/SMS=0, SCS=1)


class SCSController:
    def __init__(self,devicename,baudrate):
        self.devicename = devicename
        self.baudrate = baudrate
   
        # Initialize PortHandler instance
        # Set the port path
        # Get methods and members of PortHandlerLinux or PortHandlerWindows
        self.portHandler = PortHandler(devicename)

        # Initialize PacketHandler instance
        # Get methods and members of Protocol
        self.packetHandler = PacketHandler(protocol_end)

        # Initialize GroupSyncWrite instance
        self.groupSyncWrite = GroupSyncWrite(self.portHandler, self.packetHandler, ADDR_STS_GOAL_POSITION, 2)

    def init(self):
        # Open port
        if self.portHandler.openPort():
            print("Succeeded to open the port")
        else:
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            quit()

        # Set port baudrate
        if self.portHandler.setBaudRate(BAUDRATE):
            print("Succeeded to change the baudrate")
        else:
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            quit()
    def SyncWrite(self,id,position,speed,acc):
        for index in range(0,id.length):
            # Allocate goal position value into byte array
            param_goal_position = [SCS_LOBYTE(position[index]), SCS_HIBYTE(position[index])]

            # Add SCServo#1 goal position value to the Syncwrite parameter storage
            scs_addparam_result = self.groupSyncWrite.addParam(SCS1_ID, param_goal_position)
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % SCS1_ID)
                quit()

            # Add SCServo#2 goal position value to the Syncwrite parameter storage
            scs_addparam_result = self.groupSyncWrite.addParam(SCS2_ID, param_goal_position)
            if scs_addparam_result != True:
                print("[ID:%03d] groupSyncWrite addparam failed" % SCS2_ID)
                quit()

            # Syncwrite goal position
            scs_comm_result = self.groupSyncWrite.txPacket()
            if scs_comm_result != COMM_SUCCESS:
                print("%s" % self.packetHandler.getTxRxResult(scs_comm_result))

            # Clear syncwrite parameter storage
            self.groupSyncWrite.clearParam()
        
    def ReadPosition(self,id):
        # Read SCServo present position
        scs_present_position_speed, scs_comm_result, scs_error = self.packetHandler.read4ByteTxRx(self.portHandler, id, ADDR_STS_PRESENT_POSITION)
        if scs_comm_result != COMM_SUCCESS:
            print(self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print(self.packetHandler.getRxPacketError(scs_error))

        scs_present_position = SCS_LOWORD(scs_present_position_speed)
        scs_present_speed = SCS_HIWORD(scs_present_position_speed)
      
        return scs_present_position,scs_present_speed

    def WritePosition(self,id,position):
        # Write SCServo goal position
        scs_comm_result, scs_error = self.packetHandler.write2ByteTxRx(self.portHandler, id, ADDR_STS_GOAL_POSITION, position)
        if scs_comm_result != COMM_SUCCESS:
            print("%s" %  self.packetHandler.getTxRxResult(scs_comm_result))
        elif scs_error != 0:
            print("%s" % self. packetHandler.getRxPacketError(scs_error))

    def Close(self):
        # Close port
        self.portHandler.closePort()


