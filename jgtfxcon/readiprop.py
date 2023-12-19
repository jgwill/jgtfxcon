import os
import json

def read_json_file(filename):
  try:       
    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.realpath(__file__))
  except:
    script_dir = os.path.dirname(os.path.realpath("."))
    
  # Construct the full file path
  file_path = os.path.join(script_dir, filename)

  # Read the JSON file
  with open(file_path, 'r') as f:
    data = json.load(f)

  return data

def readiprop(instrument):
  i=instrument.replace("/","-")
  # Use the function
  data = read_json_file('iprop.json')
  return data[i]

def get_pips(instrument):
  return readiprop(instrument)['pips']
# Use the function
#data = read_json_file('iprop.json')

#print(data)