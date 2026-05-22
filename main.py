from machine import ADC, Pin, SPI, PWM
from time import sleep
from lib.lib_mcp3008 import MCP3008
from lib.lib_lcd import CharLCD
from lib.lib_qre1113 import get_error
from lib.lib_button_update import update_buttons_states
from lib.lib_motor import Motor

#CONST
SPEED = 50000
TRESHOLD = 900

#PID
KP = 4500
KD = 5000

KI = 0
last_error = 0
sum_errors = 0

# Variables

rotation_list = []

buttons = [0,0,0]

lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

motor_left = Motor(1, 0, 1000)
motor_right = Motor(5, 3, 1000)

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
        error = get_error(TRESHOLD)
        
        if error == 999 :
            error = last_error
        
        P = KP * error
        sum_errors += error
        I = KI * sum_errors
        D = KD * (error - last_error)
        
        correction = P + I + D
        last_error = error
        
        speed_motor_left = int(SPEED - correction)
        speed_motor_right = int(SPEED + correction)
        
        speed_motor_left = max(0, min(speed_motor_left, 65535))
        speed_motor_right = max(0, min(speed_motor_right, 65535))
                
        lcd.clear()
        lcd.set_line(0)
        lcd.message(str(error))
        
        motor_left.Forward(speed_motor_left)
        motor_right.Forward(speed_motor_right)
                
    
   

    
    
    
    
    
    
    
    