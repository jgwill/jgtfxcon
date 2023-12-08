import subprocess

cli_path = "/home/jgi/.local/bin/jgtfxcli"
instrument = "EUR/USD"
timeframe = "H1"
quote_count = 8000
verbose_level=0
bash_command_to_run = f"pwd;{cli_path} -i '{instrument}' -t '{timeframe}' -c {quote_count} -o -v {verbose_level}"

#and the new variable cli_path = "/home/jgi/.local/bin/jgtfxcli" will be included in existing

powershell_command = "wsl.exe bash -c \"" + bash_command_to_run + "\""
result = subprocess.run(["pwsh.exe", "-Command", powershell_command], stdout=subprocess.PIPE, shell=True)

print(result.stdout.decode('utf-8'))
