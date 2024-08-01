# sample_call.py

import os,sys
import requests
import argparse

def main():
	parser=argparse.ArgumentParser(description='Process command parameters.')
	parser.add_argument('-i','--instrument', type=str, help='Instrument')
	parser.add_argument('-s','--stop', type=float, help='Stop level')
	#flag demo
	parser.add_argument('-d','--demo', action='store_true', help='Demo mode')
	
	args=parser.parse_args()
	from jgtutils.jgtcommon import readconfig
	config=readconfig(demo=True if args.demo else False)
	user_id = config['user_id']
	password = config['password']
	url = config['url']
	connection = config['connection']
	account = config['account']
	if not all([user_id, password, url, connection]):
		print("Please set the environment variables: USER_ID, PASSWORD, URL, CONNECTION")
		return

	# Get input from the user
	
	instrument = input("Enter the instrument: ") if not args.instrument else args.instrument

	stop = input("Enter the stop level: ") if not args.stop else args.stop
	
	# Prepare the payload
	payload = {
		"user_id": user_id,
		"password": password,
		"url": url,
		"connection": connection,
		"session_id": "",  # Assuming session_id and pin are optional or can be empty
		"pin": "",
		"instrument": instrument,
		"account": account,  # Assuming account is optional or can be empty
		"stop": stop,
		"demo": True if args.demo else False
	}
	print(payload)
	#exit(0)

	# Call the REST API
	response = requests.post('http://127.0.0.1:5000/set_stop', json=payload)

	# Print the response
	if response.status_code == 200:
		print("Stop level set successfully")
	else:
		print(f"Error: {response.json().get('error')}")

if __name__ == '__main__':
	main()