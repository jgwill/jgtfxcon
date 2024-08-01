# sample_call.py

import os
import requests

def main():
	# Read environment variables
	user_id = os.getenv('user_id')
	password = os.getenv('password')
	url = os.getenv('url')
	connection = os.getenv('connection')
	account = os.getenv('account')
	#print(user_id, password, url, connection)

	if not all([user_id, password, url, connection]):
		from jgtutils.jgtcommon import readconfig
		config=readconfig()
		user_id = config['user_id']
		password = config['password']
		url = config['url']
		connection = config['connection']
		account = config['account']
		if not all([user_id, password, url, connection]):
			print("Please set the environment variables: USER_ID, PASSWORD, URL, CONNECTION")
			return

	# Get input from the user
	instrument = input("Enter the instrument: ")
	stop = input("Enter the stop level: ")

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
		"stop": stop
	}

	# Call the REST API
	response = requests.post('http://127.0.0.1:5000/set_stop', json=payload)

	# Print the response
	if response.status_code == 200:
		print("Stop level set successfully")
	else:
		print(f"Error: {response.json().get('error')}")

if __name__ == '__main__':
	main()