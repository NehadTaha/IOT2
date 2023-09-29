#!/usr/bin/env python
import ADC0832
import time
import os
import RPi.GPIO as GPIO
import math
from rpi_lcd import LCD

#set the mode
GPIO.setmode(GPIO.BCM)
lcd=LCD()
#Assign pins to the components
Buzzer = 12
Led = 25
BLUE_BUTTON = 24
RED_BUTTON = 23
# Initiate the thresheld
threshold=40.0

#Global variable
alarm_enabled = True

# A function to set up the components
def init():
    ADC0832.setup()
    GPIO.setup(Buzzer, GPIO.OUT)
    GPIO.setwarnings(False)
    GPIO.setup(Led,GPIO.OUT)
    GPIO.setup(BLUE_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RED_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BLUE_BUTTON, GPIO.FALLING, callback=enable_alarm, bouncetime=300)
    GPIO.add_event_detect(RED_BUTTON, GPIO.FALLING, callback=disable_alarm, bouncetime=300)

   # Enabled the alarm 
def enable_alarm(channel):
    global alarm_enabled
    alarm_enabled = True
    GPIO.output(Buzzer, GPIO.HIGH)
    
   #Disabled the alarm 
def disable_alarm(channel):
    global alarm_enabled
    alarm_enabled = False
    GPIO.output(Buzzer, GPIO.LOW)
#Photoresistor function to get the light status
def photoresistor():
    res_ph = ADC0832.getADC(1)
    vol = 3.3/255 * res_ph
     #Check the lux if <10 then it is dark
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
    
    # the thermistor function to get the actual temperature
def thermistor():
        res_th=ADC0832.getADC(0)
        vr=3.3 * float(res_th)/255
        if vr >= 3.3:
            return vr
        else:
          # Sleep for 1 second to avoid continuous error messages
               
            Rt = 10000 * vr / (3.3 - vr)
            if Rt==24:
                return Rt
            else:
                temp = 1/(((math.log(Rt / 10000)) / 3950) + (1 / (273.15+25)))
                
                print ('Rt : %.2f' %Rt)
                Cel = temp - 273.15
                
                    
                Fah = Cel * 1.8 + 32
            print ('Celsius: %.2f C  Fahrenheit: %.2f F' % (Cel, Fah))
           
            lcd.text('Th:{:.1f} T:{:.2f}'.format(threshold, Cel), 1)
            
            if alarm_enabled:
                # Check if the temperature is up or equal to the thredsheld then turn on the buzzer
                if Cel >= threshold:
                    
                    GPIO.output(Buzzer, GPIO.HIGH)
                else:
                     GPIO.output(Buzzer, GPIO.LOW)
            else:
                GPIO.output(Buzzer, GPIO.LOW)
            
            time.sleep(1)
      
# loop function
def loop():
    while True:
        print(threshold)
        photoresistor()
        thermistor()
           
      

if __name__ == '__main__':
    init()
    
    try:
        loop()
    except KeyboardInterrupt:
        ADC0832.destroy()
         
        print ('The end !')
    finally:
        GPIO.cleanup()
        lcd.clear()





