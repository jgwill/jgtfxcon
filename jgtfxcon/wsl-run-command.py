import subprocess



def jgtfxcli_wsl(cli_path, instrument, timeframe, quote_count, verbose_level):
  bash_command_to_run = f"pwd;{cli_path} -i '{instrument}' -t '{timeframe}' -c {quote_count} -o -v {verbose_level}"
  powershell_command = "wsl.exe bash -c \"" + bash_command_to_run + "\""
  result = subprocess.run(["pwsh.exe", "-Command", powershell_command], stdout=subprocess.PIPE, shell=True)
  return result.stdout.decode('utf-8')

# Use the function
cli_path = "/home/jgi/.local/bin/jgtfxcli"
instrument = "EUR/USD"
timeframe = "H1"
quote_count = 8000
verbose_level = 0

output = jgtfxcli_wsl(cli_path, instrument, timeframe, quote_count, verbose_level)
print(output)