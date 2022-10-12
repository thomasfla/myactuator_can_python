

#configure can before: 
#  sudo modprobe peak_usb
#  sudo ip link set can0 up type can bitrate 1000000
import can
from IPython import embed
import struct
import time
from math import pi, sin

import socket
import math
import json
from time import sleep
 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

bustype = 'socketcan'
channel = 'can0'
ID = 1

readPosition = can.Message(is_extended_id=False, arbitration_id= 0x140+ID,data=[0x60, 0, 0, 0, 0, 0, 0, 0])
motorRunningCommand = can.Message(is_extended_id=False, arbitration_id= 0x140+ID,data=[0x88, 0, 0, 0, 0, 0, 0, 0])


bus = can.Bus(channel=channel, interface=bustype)

bus.send(motorRunningCommand)
bus.recv()
t=0;



def canSend(data):
    bus.send(can.Message(is_extended_id=False, arbitration_id= 0x140+ID,data=data))
    ans = bus.recv(0.01)
    return (ans.data)
def sendCurrent(i):   
    return (canSend(struct.pack("Bxxxhxx",0xa1,int(i * 2000/33)))) #TorqueClosedLoopControlCommand
    
   

#read gains
print (canSend([0x30,0,0,0,0,0,0,0]).hex()) #pos Kp
print (canSend([0x31,0,0,0,0,0,0,0]).hex()) #pos Ki
print (canSend([0x32,0,0,0,0,0,0,0]).hex()) #vel Kp
print (canSend([0x33,0,0,0,0,0,0,0]).hex()) #vel Ki
print (canSend([0x34,0,0,0,0,0,0,0]).hex()) #cur Kp
print (canSend([0x35,0,0,0,0,0,0,0]).hex()) #cur Ki

#overwrite pos vel gain to 0
print (canSend([0x36,0,0,0,0,0,0,0]).hex()) #vel Kp
print (canSend([0x37,0,0,0,0,0,0,0]).hex()) #vel Ki
print (canSend([0x38,0,0,0,0,0,0,0]).hex()) #cur Kp
print (canSend([0x39,0,0,0,0,0,0,0]).hex()) #cur Ki


#read again
print (canSend([0x30,0,0,0,0,0,0,0]).hex()) #pos Kp
print (canSend([0x31,0,0,0,0,0,0,0]).hex()) #pos Ki
print (canSend([0x32,0,0,0,0,0,0,0]).hex()) #vel Kp
print (canSend([0x33,0,0,0,0,0,0,0]).hex()) #vel Ki
print (canSend([0x34,0,0,0,0,0,0,0]).hex()) #cur Kp
print (canSend([0x35,0,0,0,0,0,0,0]).hex()) #cur Ki
# ~ break


position = 0.0 
while(1):
    
    bus.send(readPosition)
    bus.recv()
    i_ref = 0.8*sin(2*pi*1.0*t)
    ans = sendCurrent(i_ref)
    if (ans[0] == 0x60):
        data = struct.unpack("IxxxB",ans) 
        position = 2*pi*0.00000001 * (data[0] if data[1] == 0 else -data[0])
        data = struct.unpack("IxxxB",ans) 
    if (ans[0] == 0xA1):
        data = struct.unpack("Bhhh",ans) 
        
        print (data)
 
        js = {
            "timestamp": t,
            "test_data": {
                "temp": data[0],
                "i_ref":i_ref,
                "i":data[1],
                "v":data[2],
                "p":data[3]
                }
            }
        sock.sendto( json.dumps(js).encode(), ("127.0.0.1", 9870) )
    #print(position)
    #time.sleep(0.01)
    bus.recv(0.001)
    bus.recv(0.001)

    t+=0.002
    # ~ embed()
    
