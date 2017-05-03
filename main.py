import time

import urequests
#import requests as urequests

import dht,machine,network

V = "0.15"

dhts = {}
def dht22(pin):
	#return '{{"temperature":{},"humidity":{}}}'.format(12, 34)
	if not pin in dhts:
		d = dht.DHT22(machine.Pin(pin))
		dhts[pin] = d
	else:
		d = dhts[pin]
	d.measure()
	return '{{"temperature":{},"humidity":{}}}'.format(d.temperature(), d.humidity())
analogs = {}
def analog(pin):
	if not pin in analogs:
		port = machine.ADC(pin)
		analogs[pin] = port
	else:
		port = analogs[pin]
	value = port.read()
	return '{{"analog":{}}}'.format(value)
interrupts = {}
interrupt_values = {}
def callback(i):
	global interrupt_values
	interrupt_values[i]+=1
def callback0(pin):
	callback(pin)
def callback1(pin):
	callback(pin)
def callback2(pin):
	callback(pin)
def callback3(pin):
	callback(pin)
def interrupt(pin, i, callback):
	if not pin in interrupts:
		port = machine.Pin(pin, machine.Pin.IN, machine.Pin.PULL_UP)
		port.irq(trigger=machine.Pin.IRQ_FALLING, handler=callback)
		interrupts[pin] = port
		interrupt_values[i] = 0
	else:
		port = interrupts[pin]
	count = interrupt_values[i]
	interrupt_values[i] = 0
	return '{{"interrupt":{}}}'.format(count)
def interrupt0(pin):
	return interrupt(pin, 0, callback0)
def interrupt1(pin):
	return interrupt(pin, 1, callback1)
def interrupt2(pin):
	return interrupt(pin, 2, callback2)
def interrupt3(pin):
	return interrupt(pin, 3, callback3)
AVAILABLE_SENSORS = {
	"dht22": dht22,
	"analog": analog,
	"interrupt0": interrupt0,
	"interrupt1": interrupt1,
	"interrupt2": interrupt2,
	"interrupt3": interrupt3,
}
configured_sensors = []


#uniq = 1337
uniq = int.from_bytes(machine.unique_id(),'little')
host = "http://192.168.2.30:5000"
#host = "http://192.168.2.53:5000"
url = host + "/iot/" + str(uniq) + "/{}/{}/"
register_url = host + "/iot/register/"
error_url = host + "/iot/" + str(uniq) + "/error/"
headers = {'Content-Type': 'application/json'}
registered = False

def http(data, pin, sensor):
	return urequests.post(url.format(sensor, pin), data=data, headers=headers).json()

def register():
	data = '{{"board":{},"v":{}}}'.format(uniq, V)
	response = urequests.post(register_url, data=data, headers=headers)
	return response.json()

def error(message):
	response = urequests.post(error_url, data=message, headers=headers)

def wifi_connect():
	ap_if = network.WLAN(network.AP_IF)
	ap_if.active(False)
	sta_if = network.WLAN(network.STA_IF)
	sta_if.active(True)
	
	if not sta_if.isconnected():
		print("connecting...")
		sta_if.connect("<ssid>", "<PSK>")
		while not sta_if.isconnected():
			time.sleep_ms(500)
	print("wifi: ", sta_if.ifconfig())

def collect_data():
	interval = 15
	while True:
		for func, pin, sensor in configured_sensors:
			data = func(pin)
			#print(data)
			try:
				result = http(data, pin, sensor)
				if "interval" in result:
					interval = result["interval"]
					print("new interval: "+str(interval))
			except Exception as e:
				print("Exception!: "+str(e))
				try:
					error('{"EXCEPTION":"' + str(e) + '"}')
				except:
					pass
		time.sleep(interval)

def initialize():
	wifi_connect()
	while True:
		try:
			sensors = register()
			if sensors:
				for sensor in sensors:
					if not sensor in AVAILABLE_SENSORS:
						error('{"NOT_IMPLEMENTED":"'+sensor+': '+str(sensors[sensor])+'"}')
					else:
						for pin in sensors[sensor]:
							configured_sensors.append((AVAILABLE_SENSORS[sensor], pin, sensor))
				registered = True
				break
		except:
			time.sleep(2)

####
initialize()
#print(configured_sensors)
collect_data()
