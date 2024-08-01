# stop_manager.py

import threading
from forexconnect import ForexConnect, Common
import common_samples
from SetStop import check_trades  # Import necessary methods

class StopRequest:
	def __init__(self, user_id, password, url, connection, session_id, pin, instrument, account, stop):
		self.user_id = user_id
		self.password = password
		self.url = url
		self.connection = connection
		self.session_id = session_id
		self.pin = pin
		self.instrument = instrument
		self.account = account
		self.stop = stop

class StopManager:
	def __init__(self, request: StopRequest):
		self.request = request

	def set_stop(self):
		if not self.request.stop:
			raise ValueError("Stop level must be specified")

		with ForexConnect() as fx:
			fx.login(self.request.user_id, self.request.password, self.request.url, self.request.connection, 
					 self.request.session_id, self.request.pin, common_samples.session_status_changed)

			account = Common.get_account(fx, self.request.account)
			print("AccountID='{0}'".format(account.account_id))
			if not account:
				raise Exception(f"The account '{self.request.account}' is not valid")

			table_manager = fx.table_manager
			check_trades(fx, table_manager, self.request.account)