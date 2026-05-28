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

def get_normalize_values(calibration_clear, calibration_delta):
    raw_values = read_all_qre1113()
    normalize_values = [0,0,0,0,0,0,0,0]
    for i in range(8):
        normalize_values[i] = max(0, raw_values[i] - calibration_clear[i])
        normalize_values[i] /= calibration_delta[i]
    return normalize_values

def get_error(calibration_clear, calibration_delta):
    normalize_values = get_normalize_values(calibration_clear, calibration_delta)
    error = 0
    counter = 0
    QRE1113_Weights = [-4,-3,-2,-1,1,2,3,4]
    for i in range(8) :
        counter += normalize_values[i]
        error += normalize_values[i] * QRE1113_Weights[i]
    if counter < 0.1 :
        return 999
    if counter > 0 :
        error /= counter
    return error