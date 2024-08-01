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
        "docker", "run", "--rm",
        "-v", f"{config_path}:/root/.jgt/config.json",
        "-v", f"{data_path}:/data",
        "jgwill/jgt:fxcon",
        "jgtfxcli"
    ]

    # Append all arguments passed to fxcli to the docker command
    docker_command.extend(sys.argv[1:])

    # Run the Docker command
    subprocess.run(docker_command)

if __name__ == "__main__":
    main()