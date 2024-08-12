import subprocess
import os
import sys

def main():
    system_settings_path = os.path.join('/etc', 'jgt', 'settings.json')
    home_dir = os.path.expanduser("~")
    home_config_path = os.path.join(home_dir, ".jgt", "config.json")
    home_settings_path = os.path.join(home_dir, ".jgt", "settings.json")
    data_path = os.path.join(home_dir, ".jgt", "nds")
    dk_data_path = "/nds"
    full_data_path = os.path.join(home_dir, ".jgt", "fds")
    dk_full_data_path = "/fds"
    #mkdir local path
    os.makedirs(data_path, exist_ok=True)
    os.makedirs(full_data_path, exist_ok=True)
    current_directory=os.getcwd()
    
    docker_command = [
        "docker", "run"]
    
    if "--bash" in sys.argv:
        docker_command.append("-it")
    
    cli_to_run = "jgtfxcli"
    #we want to specify alternatively the cli to run and pass its arguments when running the docker container
    possible_clis=["fxtr","fxrmorder","fxaddorder","fxreport"]
    for cli in possible_clis:
        if cli in sys.argv:
            cli_to_run=cli
            #remove it from the arguments list
            sys.argv.remove(cli)
            break

    docker_image_repo_tag = "jgwill/jgt:fxcon"
    dk_home_path="/home/user"
    
    # "-v", f"{home_settings_path}:/etc/jgt/settings.json",
    docker_command = docker_command+       [ "--rm",
        "-v", f"{home_config_path}:{dk_home_path}/.jgt/config.json",
        "-v", f"{home_settings_path}:{dk_home_path}/.jgt/settings.json",
        "-v", f"{system_settings_path}:/etc/jgt/settings.json",
        "-v", f"{data_path}:{dk_data_path}",
        "-e", f"JGTPY_DATA={dk_data_path}",
        "-v", f"{full_data_path}:{dk_full_data_path}",
        "-e", f"JGTPY_DATA_FULL={dk_full_data_path}",
        "-v",f"{current_directory}:/work",
        docker_image_repo_tag]

    # Check if --bash is present in the arguments
    if "--bash" in sys.argv:
        docker_command.append("bash")
        # Remove --bash from the arguments list
        sys.argv.remove("--bash")
    else:
        docker_command.append(cli_to_run)
    print(f"Running Docker command: {' '.join(docker_command)}")
    # Append all remaining arguments passed to fxcli to the docker command
    docker_command.extend(sys.argv[1:])

    # Run the Docker command
    subprocess.run(docker_command)

if __name__ == "__main__":
    main()