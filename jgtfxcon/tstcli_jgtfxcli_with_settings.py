
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from jgtfxcli import run

def main():
  run(enable_specified_settings=True)

if __name__ == "__main__":
  main()
  