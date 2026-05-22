from machine import Pin
from time import sleep

pin13 = Pin(13, Pin.IN, Pin.PULL_UP) # PULL_UP invers output, buttons don't work with this
pin14 = Pin(14, Pin.IN, Pin.PULL_UP)
pin15 = Pin(15, Pin.IN, Pin.PULL_UP)

def update_buttons_states():
    # Set the button_1 button_2 button_3 to the values of the buttons
    buttons = [0,0,0]
    
    if pin13.value() == 0 :
        buttons[0] = 1
    else :
        buttons[0] = 0
        
    if pin14.value() == 0 :
        buttons[1] = 1
    else :
        buttons[1] = 0
        
    if pin15.value() == 0 :
        buttons[2] = 1
    else :
        buttons[2] = 0
        
    return buttons
        
    