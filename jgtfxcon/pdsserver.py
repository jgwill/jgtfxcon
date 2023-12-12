from flask import Flask, jsonify, request
#from jgtfxcon import sc,up,h,stay

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import warnings

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=RuntimeWarning, module="importlib._bootstrap")
    # your code here# your code here

from subprocess import check_output
import shlex


# from jgtfxcon.JGTPDS import getPH, mk_fn, mk_fullpath,getPH_to_filestore as ph2fs,getPH_from_filestore,get_instrument_properties

#stayConnectedSetter(True)

app = Flask(__name__)
#stayConnectedSetter(True)


#@app.route('/stay',method=['GET'])
#def fetch_stay():
#    data = request.json
#    stayConnectedSetter(True)
#    return '{}'

@app.route('/getPH', methods=['POST'])
def fetch_getPH():
    data = request.json
    instrument = data['instrument']
    timeframe = data['timeframe']
    #result = h(instrument, timeframe)
    #df = getPH_from_filestore(instrument, timeframe)
    from JGTPDS import getPH
    df = getPH(instrument, timeframe)
    result = df.to_csv()
    print(result)
    #return jsonify(result)  # Assuming the result can be serialized into JSON
    return result  # Assuming the result can be serialized into JSON


@app.route('/getPH_from_filestore', methods=['POST'])
def fetch_getPH_from_filestore():
    data = request.json
    instrument = data['instrument']
    timeframe = data['timeframe']
    quiet = data.get('quiet', True)  # Optional parameter, defaults to True
    compressed = data.get('compressed', False)  # Optional parameter, defaults to False
    with_index = data.get('with_index', True)  # Optional parameter, defaults to True
    from JGTPDS import getPH_from_filestore
    df = getPH_from_filestore(instrument, timeframe, quiet, compressed, with_index)
    return df.to_json(orient='split')


@app.route('/h', methods=['POST'])
def fetch_h():
    data = request.json
    instrument = data['instrument']
    timeframe = data['timeframe']
    from JGTPDS import getPH_from_filestore
    df = getPH_from_filestore(instrument, timeframe)
    return df.to_json(orient='split')


@app.route('/cli', methods=['POST'])
def run_jgtcli():
    data = request.json
    instrument = data['instrument']
    timeframe = data['timeframe']

    # Optional parameters with default values
    datefrom = data.get('datefrom', None)
    dateto = data.get('dateto', None)
    quote_count_default = 335
    qt = data.get('quote_count', quote_count_default)
    quote_count = ''
    if data.get('quote_count') and quote_count_default != data.get('quote_count'):
        quote_count = '-c ' + str(qt)
    #quote_count = '-c ' if data.get('quote_count', 335) else ''
    #output = '-o' if data.get('output', False) else ''
    # cds = '-cds' if data.get('cds', False) else ''
    verbose = '-v %s' % data.get('verbose', 0)

    # Construct the command
    cmd = f'jgtfxcli -i {instrument} -t {timeframe} {quote_count} -o  {verbose}'
    # cmd = f'jgtfxcli -i {instrument} -t {timeframe} -o {cds} {verbose}'


    if datefrom:
        cmd += f' -s "{datefrom}"'
    if dateto:
        cmd += f' -e "{dateto}"'

    # Execute the command
    print("==================CLI===================")
    print(cmd)
    print("========================================")

    try:
        result = check_output(shlex.split(cmd)).decode('utf-8')
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e), 'cmd':cmd})


@app.route('/init', methods=['GET'])
def run_init():
    cmd = 'jgtfxcli --iprop'
    # Execute the command
    print("==================CLI===================")
    print(cmd)
    print("========================================")

    try:
        result = check_output(shlex.split(cmd)).decode('utf-8')
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e), 'cmd':cmd})


@app.route('/mk_fn', methods=['GET'])
def fetch_mk_fn():
    instrument = request.args.get('instrument')
    timeframe = request.args.get('timeframe')
    ext = request.args.get('ext')
    from JGTPDS import mk_fn
    result = mk_fn(instrument, timeframe, ext)
    return jsonify({'filename': result})

# More routes for other functions...

@app.route('/iprop', methods=['POST'])
def fetch_get_instrument_properties():
    data = request.json
    instrument = data['instrument'].replace('-','/')
    from JGTPDS import get_instrument_properties
    properties = get_instrument_properties(instrument,from_file=True)
    return jsonify({'properties': properties})


if __name__ == '__main__':
    app.run(debug=True)


