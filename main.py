import dht,machine
import urequests
import network
import time

uniq = int.from_bytes(machine.unique_id(),'little')
host = "http://192.168.2.30:5000"
url = host + "/iot/" + str(uniq) + "/"
register_url = host + "/iot/register/"
registered = False

def http(url,t,h):
	headers = {'Content-Type': 'application/json'}
	data ="{{'temperature':{},'humidity':{}}}".format(d.temperature(),d.humidity())
	return urequests.post(url, data=data, headers=headers).text
def register(register_url, uniq):
	headers = {'Content-Type': 'application/json'}
	data = "{{'board':{}}}".format(uniq)
	response = urequests.post(register_url, data=data, headers=headers)
	return response.text == "ok" or response.json()["success"]
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

wifi_connect()
registered = register(register_url, uniq)

d = dht.DHT22(machine.Pin(12))

while True:
	d.measure()
	try:
		http(url, d.temperature(), d.humidity())
	except Exception as e:
		print("Exception!: "+str(e))
	time.sleep(15)
