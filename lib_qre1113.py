from machine import Pin, SPI
from lib_mcp3008 import MCP3008
from lib_lcd import CharLCD

#LCD Settings
lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

#MCP3008 settings
spi = SPI(0, sck=Pin(18),mosi=Pin(19),miso=Pin(16), baudrate=100000)
cs = Pin(22, Pin.OUT)
chip = MCP3008(spi, cs)

def read_all_qre1113():
    values = [0,0,0,0,0,0,0,0]
    for i in range(0,8):
        values[i] = chip.read(i)
    return values

def get_value_binary_format(calibration):
    values = read_all_qre1113()
    values_binary = [0,0,0,0,0,0,0,0]
    for i in range(0,8):
        if values[i] >= calibration[i] * 0.88 :
            values_binary[i] = 1
    return values_binary

def get_error(calibration):
    list_values_binary = get_value_binary_format(calibration)
    error = 0
    counter = 0
    QRE1113_Weights = [-4,-3,-2,-1,1,2,3,4]
    for i in range(8) :
        counter += list_values_binary[i]
        error += list_values_binary[i] * QRE1113_Weights[i]
    if counter > 0 :
        error /= counter
    return error