#!/usr/bin/env python
import ADC0832_1
import ADC0832_2
import time
import os
import RPi.GPIO as GPIO
import math
from rpi_lcd import LCD


GPIO.setmode(GPIO.BCM)
lcd=LCD()

Buzzer = 12
Led = 25
BLUE_BUTTON = 24
RED_BUTTON = 23

threshold=0

#Global variable
alarm_enabled = True


def init():
    ADC0832_1.setup()
    ADC0832_2.setup()
    GPIO.setup(Buzzer, GPIO.OUT)
    GPIO.setwarnings(False)
    GPIO.setup(Led,GPIO.OUT)
    GPIO.setup(BLUE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BLUE_BUTTON, GPIO.FALLING, callback=enable_alarm, bouncetime=300)
    GPIO.add_event_detect(RED_BUTTON, GPIO.FALLING, callback=disable_alarm, bouncetime=300)

    
def enable_alarm(channel):
    global alarm_enabled
    alarm_enabled = True
    GPIO.output(Buzzer, GPIO.HIGH)
    
    
def disable_alarm(channel):
    global alarm_enabled
    alarm_enabled = False
    GPIO.output(Buzzer, GPIO.LOW)

def photoresistor():
    res_ph = ADC0832_1.getADC(1)
    vol = 3.3/255 * res_ph
     #If the lux<10
    if res_ph < 128:
        print('dark')
        lcd.text('Status:dark', 2)
        GPIO.output(Led,GPIO.HIGH)
    else:
        print('light')
        lcd.text('Status:light', 2)
        GPIO.output(Led,GPIO.LOW)
    time.sleep(1)
        
    print ('analog value: %03d  ||  voltage: %.2fV' %(res_ph, vol))
    
def thermistor(threshold):
    try:
        res_th=ADC0832_1.getADC(0)
        vr=3.3 * float(res_th)/255
        
        if vr >= 3.3:
          # Sleep for 1 second to avoid continuous error messages
            print('vr',vr)
        else:
            Rt = 10000 * vr / (3.3 - vr)
            if Rt==0:
                return Rt
            else:
                temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
                Cel = temp - 273.15
                #Fah = Cel * 1.8 + 32
            print ('Celsius: %.2f C' %Cel)
            
            if alarm_enabled:
                
                if Cel >= threshold:
                    
                    GPIO.output(Buzzer, GPIO.HIGH)
                else:
                     GPIO.output(Buzzer, GPIO.LOW)
            else:
                GPIO.output(Buzzer, GPIO.LOW)
            
            time.sleep(1)
            lcd.text('Th:{:.1f} T:{:.2f}'.format(threshold, Cel), 1)
    except ZeroDivisionError:
            print("Division by zero")
      
def potentiometer():
    res = ADC0832_2.getADC(0)
    threshold = (res * 40)/255
    time.sleep(1)
    return threshold

def loop():
    try:
        while True:
            threshold = potentiometer()
            photoresistor()
            thermistor(threshold)
    except ZeroDivisionError:
        print("Error")
           
      

if __name__ == '__main__':
    init()
    
    try:
        loop()
    except KeyboardInterrupt:
        ADC0832_1.destroy()
        ADC0832_2.destroy()
         
        print ('The end !')
    finally:
        GPIO.cleanup()
        lcd.clear()





