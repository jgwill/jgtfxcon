import subprocess
import os
import sys

def main():
    home_dir = os.path.expanduser("~")
    config_path = os.path.join(home_dir, ".jgt", "config.json")
    data_path = os.path.join(home_dir, ".jgt", "data")
    #mkdir local path
    os.makedirs(data_path, exist_ok=True)
    
    docker_command = [
        "docker", "run"]
    
    if "--bash" in sys.argv:
        docker_command.append("-it")
        

    docker_command = docker_command+       [ "--rm",
        "-v", f"{config_path}:/etc/jgt/config.json",
        "-v", f"{data_path}:/data",
        "jgwill/jgt:fxcon"]

    # Check if --bash is present in the arguments
    if "--bash" in sys.argv:
        docker_command.append("bash")
        # Remove --bash from the arguments list
        sys.argv.remove("--bash")
    else:
        docker_command.append("jgtfxcli")
    print(f"Running Docker command: {' '.join(docker_command)}")
    # Append all remaining arguments passed to fxcli to the docker command
    docker_command.extend(sys.argv[1:])

    # Run the Docker command
    subprocess.run(docker_command)

if __name__ == "__main__":
    main()