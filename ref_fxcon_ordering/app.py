# app.py
from flask import Flask, request, jsonify
from jgt_stop_manager import JGTStopManager as StopManager

app = Flask(__name__)
stop_manager = StopManager()

@app.route('/set_stop', methods=['POST'])
def set_stop():
    data = request.get_json()
    price = data.get('price')
    if price is None:
        return jsonify({"error": "Price is required"}), 400
    result = stop_manager.set_stop(price)
    return jsonify({"message": result})

if __name__ == '__main__':
    app.run(debug=True)