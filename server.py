#!/usr/bin/python

import threading
import multiprocessing
import RPi.GPIO as GPIO
import time
import subprocess
from multiprocessing import Process, Value, Array
from datetime import datetime
from multiprocessing.pool import ThreadPool
from threading import Thread

print 'setting variables'

Pin = 21
GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
GPIO.setup(Pin, GPIO.OUT)
ip = ['192.168.0.10','192.168.0.64','192.168.0.12','192.168.0.3']
ping = "1"
pingseq = 1
online = []
timestamp = []
return_val = []
prevonline = []
nighttime = ['02','03','04','05','06','07']
value = []

#GPIO.output(Pin, GPIO.HIGH)
#time.sleep(3)
#GPIO.output(Pin, GPIO.LOW)
#time.sleep(2)
#GPIO.output(Pin, GPIO.HIGH)
#time.sleep(1)
#GPIO.output(Pin, GPIO.LOW)

for i in range(len(ip)):
    online.append(-1)
    timestamp.append(-1)
    return_val.append(-1)    
    value.append(-1)

def f(ip, ping):
    """ping worker function"""
    output = subprocess.Popen(["ping","-c", ping,"-W", "1", ip],stdout = subprocess.PIPE,shell=False)
    check = output.communicate()[0]
    check = output.returncode
    #return check

def opennight():
	print 'switching on for 30 seconds'
	GPIO.output(Pin, GPIO.LOW)
        time.sleep(30)
	print 'switching off'
        GPIO.output(Pin, GPIO.HIGH)

print 'done initializing' 

if __name__ == "__main__": 
    while True:
        hour = datetime.now().strftime('%H') #there are better ways of doig this but I'm lazy right now
	prevonline = online[:]
        pool = ThreadPool(processes=len(ip)) #sets thread number
        for i in range(len(ip)):
            timestamp[i] = int(round(time.time())) #gets time in arra
            value[i] = pool.apply_async(f, args=(ip[i], ping)) #starts threads and assigns to array
        for i in range(len(ip)):
            return_val[i] = value[i].get() #gets values
	    if return_val[i] == 0:
                online[i] = timestamp[i] #updates timestamp if connected
            if online[i]-prevonline[i] > 30: #30 second timeout
		print 'checking nighttime'
                if hour in nighttime and online[i]-prevonline[i] > 300: #50 second timeout (20 seconds plus 30 seconds on the opennight routine
		    opennight()
		else:
                    #GPIO.output(Pin, GPIO.LOW) #this opens the door during daytime
                    #time.sleep(0.5)  #comment out if you just want the lights
		    GPIO.output(Pin, GPIO.LOW)
        if sum(return_val) < len(ip):
		if hour in nighttime:
			GPIO.output(Pin, GPIO.HIGH) #this sets the lights during nighttime
		else:
			GPIO.output(Pin, GPIO.LOW) #during daytime
	else:
		deviceoffline = 0
		for i in range(len(ip)):
			if timestamp[i]-prevonline[i] > 1200: #changing this value to two hours for power saving
				deviceoffline = deviceoffline + 1 #checks for devices
		if deviceoffline == len(ip):
			print deviceoffline #if no devices are found the it turns everything off
			GPIO.output(Pin, GPIO.HIGH)
	pool.terminate() #terminates the threads
	print 'devicenum'
	print sum(return_val)
        print 'return_val'
        print return_val
        print 'time'
        print timestamp
	print 'prevonline'
	print prevonline
        print 'online'
        print online
	time.sleep(0.8)

#	hour = datetime.now().strftime('%H')
#    	prevdevices2 = prevdevices
#	prevdevices = devices
#	devices = []
#	for j in range(pingseq):
#	    	for i in range(len(ip)):
#	        	p = Process(target=f, args=(num, ip[i], ping))
#	        	p.start()
#        		p.join()
#			print num.value
#	        	if num.value == 0 and not (ip[i] in devices):
#				devices.append(ip[i])
#				print ip[i]
#		    #GPIO.output(Pin, GPIO.HIGH)
#    	print devices
#    	if len(devices) == 0:
#	    if alreadyoff == 1:
#	    	GPIO.output(Pin, GPIO.LOW)
#		ping = "1"
#	    else:
#		alreadyoff = 1
#		time.sleep(1)
#	elif hour in nighttime:
#		if len(prevdevices) < len(devices) and len(prevdevices2) == len(prevdevices):
#			GPIO.output(Pin, GPIO.HIGH)
#			time.sleep(30)
#			GPIO.output(Pin, GPIO.LOW)
#	else:
#		if len(prevdevices) < len(devices) and len(prevdevices2) == len(prevdevices):
#			GPIO.output(Pin, GPIO.LOW)
#			time.sleep(0.3)
#                        GPIO.output(Pin, GPIO.HIGH)
#		else:
#			GPIO.output(Pin, GPIO.HIGH)
#
#    	elif int(float(hour)) > 7 or int(float(a)) < 3:
#    	    GPIO.output(Pin, GPIO.HIGH)
#	    ping = "5"
#	    alreadyoff = 0
#	else:
#	    GPIO.output(Pin, GPIO.LOW)
#	if hour in nighttime:
#		if len(prevdevices) < len(devices) and len(prevdevices2) == len(prevdevices):
#			GPIO.output(Pin, GPIO.HIGH)
#			time.sleep(30)
#			GPIO.output(Pin, GPIO.LOW)
#			pingseq = 3
#		else:
#			GPIO.output(Pin, GPIO.LOW)
#			pingseq = 3
#	else:
#		if len(devices) == 0:
#			GPIO.output(Pin, GPIO.LOW)
#			pingseq = 1
#		elif len(prevdevices) < len(devices) and len(prevdevices2) == len(prevdevices):
#			GPIO.output(Pin, GPIO.LOW)
#			time.sleep(0.5)
#			GPIO.output(Pin, GPIO.HIGH)
#			pingseq = 5
#		else:
#			GPIO.output(Pin, GPIO.HIGH)
#			pingseq = 5

