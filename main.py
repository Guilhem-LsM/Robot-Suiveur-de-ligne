from machine import ADC, Pin, SPI, PWM, Timer
from time import sleep
import os
import utime
import json
from lib.lib_mcp3008 import MCP3008
from lib.lib_lcd import CharLCD
from lib.lib_qre1113 import get_error
from lib.lib_button_update import update_buttons_states
from lib.lib_motor import Motor
import time

#CONST
SPEED_BASE = 50000
TRESHOLD = 900

#PID
KP = 4500
KD = 5000
KI = 0
KS = 1

error = 0
last_error = 0
sum_errors = 0
correction = 0
speed_motor_left = 0
speed_motor_right = 0

# Variables

rotation_list = []

buttons = [0,0,0]

lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

motor_left = Motor(1, 0, 1000)
motor_right = Motor(5, 3, 1000)

adc_BPV11 = ADC(2) #BPV11

state = "start"

tesh_BPV11 = adc_BPV11.read_u16() * 1.5

#Timer
timer_start = Timer()
timer_run = Timer()
timer_run_state = False
timer_start_state = False
start_time = 0
elapsed = 0
modulate_speed = 0

#log
log_flag = False
log_graph = [["error", "right motor speed", "left motor speed", "robot speed"],[],[],[],[],[]]

#function

def get_formatted_time():
    t = utime.localtime()
    return "{:04d}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(t[0], t[1], t[2], t[3], t[4], t[5])

def make_a_choice(t):
    global error
    global last_error
    global sum_errors
    global correction
    global speed_motor_left
    global speed_motor_right
    global log_flag
    global modulate_speed

    error = get_error(TRESHOLD)

    if error == 999 :
        error = last_error

    P = KP * error
    sum_errors += error
    I = KI * sum_errors
    D = KD * (error - last_error)

    modulate_speed = SPEED_BASE - abs(error)*KS

    correction = P + I + D
    last_error = error

    speed_motor_left = int(modulate_speed - correction)
    speed_motor_right = int(modulate_speed + correction)

    speed_motor_left = max(0, min(speed_motor_left, 65535))
    speed_motor_right = max(0, min(speed_motor_right, 65535))

    motor_left.Forward(speed_motor_left)
    motor_right.Forward(speed_motor_right)

    log_flag = True

def flash_check(t):
    global timer_start_state
    global state

    value = adc_BPV11.read_u16()
    if value > tesh_BPV11 :
        state = "run"
        timer_start.deinit()
        timer_start_state = False

file_name = "log_"+get_formatted_time()

while True :
    # start state
    if not timer_start_state :
        timer_start.init(period=1, mode=Timer.PERIODIC, callback=flash_check)
        timer_start_state = True

    if state == "start" :
        if timer_run_state :
            timer_run.deinit()
            timer_run_state = False
            with open("logs/"+file_name+".json", "w") as f :
                json.dump(log_graph, f)
            with open("logs/"+file_name+".txt", "w") as f :
                f.write("KP : " + str(KP) + "\n")
                f.write("KI : " + str(KI) + "\n")
                f.write("KD : " + str(KD) + "\n")
                f.write("SPEED_BASE : " + str(SPEED_BASE) + "\n")         

    # run State
    if state == "run" :
        if not timer_run_state :
            timer_run.init(period=10, mode=Timer.PERIODIC, callback=make_a_choice)
            timer_run_state = True
            start_time = time.ticks_ms()
        if log_flag :
            elapsed = time.ticks_diff(time.ticks_ms(), start_time)
            log_graph[1].append(elapsed)
            log_graph[2].append(error)
            log_graph[3].append(speed_motor_right)
            log_graph[4].append(speed_motor_left)
            log_graph[5].append(modulate_speed)
            log_flag = False