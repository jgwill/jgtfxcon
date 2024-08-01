# app.py
from flask import Flask, request, jsonify
from jgt_stop_manager import StopRequest, StopManager

app = Flask(__name__)

@app.route('/set_stop', methods=['POST'])
def set_stop():
  data = request.get_json()
  try:
    stop_request = StopRequest(
      user_id=data['user_id'],
      password=data['password'],
      url=data['url'],
      connection=data['connection'],
      session_id=data['session_id'],
      pin=data['pin'],
      instrument=data['instrument'],
      account=data['account'],
      stop=data['stop']
    )
    stop_manager = StopManager(stop_request)
    stop_manager.set_stop()
    return jsonify({"message": "Stop level set successfully"}), 200
  except KeyError as e:
    return jsonify({"error": f"Missing parameter: {str(e)}"}), 400
  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
  app.run(debug=True)