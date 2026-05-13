from machine import Pin, PWM
from time import sleep
from mcp3008 import MCP3008
from machine import ADC, Pin, SPI
from LCD import CharLCD

#LCD Settings
lcd = CharLCD(rs=2, en=4, d4=7, d5=8, d6=9, d7=10, cols=16, rows=2)

#MCP3008 settings
spi = SPI(0, sck=Pin(18),mosi=Pin(19),miso=Pin(16), baudrate=100000)
cs = Pin(22, Pin.OUT)
chip = MCP3008(spi, cs)

def read_all():
    values = [0,0,0,0,0,0,0,0]
    for i in range(0,8):
        values[i] = chip.read(i)
    return values

def get_value_binary(threshold):
    sleep(0.1)
    values = read_all()
    values_binary = [0,0,0,0,0,0,0,0]
    for i in range(0,8):
        if values[i] > threshold :
            values_binary[i] = 1
    print(values_binary)
    return values_binary

def get_rotate(list_binary):
    rotation = 0
    number_value = 0
    table_value_QRE1113 = [-2,-1.5,-1,-1,1,1,1.5,2]
    for i in range(8) :
        rotation += list_binary[i] * table_value_QRE1113[i]
        if list_binary[i] == 1 :
            number_value += 1
    if number_value != 0 :
        rotation /= number_value
    lcd.set_line(0) 
    lcd.message(str(rotation))
    return rotation