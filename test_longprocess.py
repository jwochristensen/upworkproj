import flask_demo
import time
import requests
import json

#error occurring: 
#Request failed: Expecting value: line 1 column 1 (char 0)

#http://127.0.0.1:5000/send_ble/
url = "http://127.0.0.1:5000/send_ble/"
payload = {"msg": "test message now"}
headers = {'Content-type': 'application/json'}


def send_ble_message(payload):
	try:
		response = requests.post(url, data=json.dumps(payload), headers=headers, verify=True)
    	response.raise_for_status()
    	print(response.json())

	except requests.exceptions.RequestException as e:
    	print(f"Request failed: {e}")
	except json.JSONDecodeError:
    	print("Invalid JSON response")


while True:

	time.sleep(2.0)

	try:
		send_ble_message(payload)

	except Exception as e:
		print(e)
		continue

