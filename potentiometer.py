#!/usr/bin/env python
import ADC0832_2
import time


def init():
	ADC0832_2.setup()



def loop():
	while True:
		res = ADC0832_2.getADC(0)
		vol = 3.3/255 * res
		print ('analog value: %03d  ||  voltage: %.2fV' %(res, vol))
		
		time.sleep(0.2)

if __name__ == '__main__':
	init()
	try:
		loop()
	except KeyboardInterrupt: 
		ADC0832_2.destroy()
		print ('The end !')

