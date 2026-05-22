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

def get_value_binary_format(threshold):
    values = read_all_qre1113()
    #print(values)
    values_binary = [0,0,0,0,0,0,0,0]
    for i in range(0,8):
        if values[i] > threshold :
            values_binary[i] = 1
    #print(values_binary)
    return values_binary

def get_error(threshold):
    list_binary = get_value_binary_format(threshold)
    rotation = 0
    number_value = 0
    table_value_QRE1113 = [-4,-3,-2,-1,1,2,3,4]
    count_zero = 0
    for i in range(8) :
        rotation += list_binary[i] * table_value_QRE1113[i]
        number_value += list_binary[i]
    if number_value != 0 :
        rotation /= number_value
    else :
        rotation = 999
    return rotation