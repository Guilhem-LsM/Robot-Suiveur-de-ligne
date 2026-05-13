from machine import Pin, PWM
from time import sleep
from mcp3008 import MCP3008
from machine import ADC, Pin, SPI
from LCD import CharLCD
from QRE1113 import get_value_binary, get_rotate
from ButtonUpdate import update_buttons_states
from Motors import Motor

# Variables

buttons = buttons = [0,0,0]

lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

SPEED = 10000

MotorLeft = Motor(1, 0, 1000)
MotorRight = Motor(5, 3, 1000)

adc_BPV11 = ADC(2) #BPV11

state = "run"

tesh_BPV11 = adc_BPV11.read_u16() * 1.5

while True :
    buttons = update_buttons_states()
    t = adc_BPV11.read_u16()
    # Start state
    if state == "start" :
        if t > tesh_BPV11 :
            print(t)
            state = "run"
            sleep(0.5)
    
    #State run
    if state == "run" :
        values = get_value_binary(400)
        rotation = get_rotate(values)
        rotation_MotorLeft = 1
        rotation_MotorRight = 1
        
        if rotation > 0 :
            rotation_MotorRight = int(2.5 - rotation*1/4)
        elif rotation < 0 :
            rotation_MotorLeft = int(2.5 - abs(rotation)*1/4)
        
        MotorLeft.Forward(rotation_MotorLeft * SPEED)
        MotorRight.Forward(rotation_MotorRight * SPEED)
        
        
        if t > tesh_BPV11 :
            print(t)
            state = "start"
            sleep(0.5)
    
   

    
    
    
    
    
    
    
    