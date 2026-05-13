from machine import ADC, Pin, SPI, PWM

class Motor:
    def __init__(self, pin_forward, pin_backward, f):
        self.forward = PWM(Pin(pin_forward))
        self.forward.freq(f)
        self.forward.duty_u16(0)
        
        self.backward = PWM(Pin(pin_backward))
        self.backward.freq(f)
        self.backward.duty_u16(0)
        
    def Forward(self, speed):
        self.backward.duty_u16(0)
        self.forward.duty_u16(speed)
    
    def Backward(self, speed):
        self.forward.duty_u16(0)
        self.backward.duty_u16(speed)