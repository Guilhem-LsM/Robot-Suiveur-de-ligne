from machine import ADC, Pin, SPI, PWM, Timer
from time import sleep
import os
import utime
import json
from lib.lib_mcp3008 import MCP3008
from lib.lib_lcd import CharLCD
from lib.lib_qre1113 import get_error, read_all_qre1113
from lib.lib_button_update import update_buttons_states
from lib.lib_motor import Motor
import time

#CONST
SPEED_BASE = 30000 #30000

#PID
KP = 4000 #3500
KD = 1650 #1400
KI = 0
KS = 0

error = 0
last_error = 0
sum_errors = 0
correction = 0
speed_motor_left = 0
speed_motor_right = 0

# Variables

rotation_list = []

calibration = [900,900,900,900,900,900,900,900]
calibration_done = False

buttons = [0,0,0]

lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

motor_left = Motor(1, 0, 1000)
motor_right = Motor(5, 3, 1000)

adc_BPV11 = ADC(2) #BPV11

state = "start"

tesh_BPV11 = adc_BPV11.read_u16() *0.2

#Timer
timer_start = Timer()
timer_run = Timer()
timer_run_state = False
timer_start_state = False
start_time = 0
elapsed = 0
modulate_speed = 0

#Stop
flag_stop = False
timer_stop_counter = 0

#log
log_flag = False
log_graph = [["error", "right motor speed", "left motor speed", "robot speed"],[],[],[],[],[]]
log_on_off = True

#function

def get_formatted_time():
    t = utime.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}_{:02d}_{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

def make_a_choice(t):
    global error
    global last_error
    global sum_errors
    global correction
    global speed_motor_left
    global speed_motor_right
    global log_flag
    global modulate_speed
    global state
    global flag_stop
    global timer_stop_counter
    
    error = get_error(calibration)
    if error == 999 :
        error = last_error
        if not flag_stop :
            flag_stop = True
            timer_stop_counter = time.ticks_ms()
        elif time.ticks_diff(time.ticks_ms(), timer_stop_counter) > 1000:
            motor_left.Forward(0)
            motor_right.Forward(0)
            state = "start"
            return
        print(time.ticks_diff(time.ticks_ms(), timer_stop_counter))
    else :
        flag_stop = False

    P = KP * error
    sum_errors += error
    I = KI * sum_errors
    D = KD * (error - last_error)

    speed_corection = 1 - KS*(error / 4)

    correction = P + I + D
    last_error = error

    speed_motor_left = int((SPEED_BASE - correction) * speed_corection)
    speed_motor_right = int((SPEED_BASE + correction) * speed_corection)

    speed_motor_left = max(0, min(speed_motor_left, 65535))
    speed_motor_right = max(0, min(speed_motor_right, 65535))

    motor_left.Forward(speed_motor_left)
    motor_right.Forward(speed_motor_right)

    log_flag = True

def flash_check(t):
    global timer_start_state
    global state
    global buttons
    buttons = update_buttons_states()
    value = adc_BPV11.read_u16()
    if value <= tesh_BPV11 or buttons[2]:
        state = "run"
        timer_start.deinit()
        timer_start_state = False

file_name = "log-"+get_formatted_time()

while True :
    # start state
    if state == "start" :
        if not timer_start_state :
            print("Start")
            lcd.clear()
            lcd.message("Start " + str(error))
            timer_start.init(period=1, mode=Timer.PERIODIC, callback=flash_check)
            timer_start_state = True
        if timer_run_state :
            timer_run.deinit()
            timer_run_state = False
            if log_on_off :
                with open("logs/"+file_name+".json", "w") as f :
                    json.dump(log_graph, f)
                with open("logs/"+file_name+".txt", "w") as f :
                    f.write("KP : " + str(KP) + "\n")
                    f.write("KI : " + str(KI) + "\n")
                    f.write("KD : " + str(KD) + "\n")
                    f.write("SPEED_BASE : " + str(SPEED_BASE) + "\n")
        buttons = update_buttons_states()
        if buttons[0] :
            calibration = read_all_qre1113()
            print(calibration)
            lcd.clear()
            lcd.message("Calibration done")
            sleep(1)
            lcd.clear()

    # run State
    if state == "run" :
        buttons = update_buttons_states()
        if buttons[1] :
            motor_left.Forward(0)
            motor_right.Forward(0)
            state = "start"
            print("tugug")
        if not timer_run_state :
            print("Run")
            lcd.clear()
            lcd.message("Run")
            timer_run.init(period=10, mode=Timer.PERIODIC, callback=make_a_choice)
            timer_run_state = True
            start_time = time.ticks_ms()
        if log_flag :
            elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            log_graph[1].append(elapsed)
            log_graph[2].append(error*1000)
            log_graph[3].append(speed_motor_right)
            log_graph[4].append(speed_motor_left)
            log_graph[5].append(modulate_speed)
            log_flag = False