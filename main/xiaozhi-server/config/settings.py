import os
from config.config_loader import read_config, get_project_dir, load_config


default_config_file = "config.yaml"
config_file_valid = False


def check_config_file():
    global config_file_valid
    if config_file_valid:
        return
    """
    Simplified configuration check, only prompts the user about the configuration file usage
    """
    custom_config_file = get_project_dir() + "data/." + default_config_file
    if not os.path.exists(custom_config_file):
        raise FileNotFoundError(
            "If the file data/.config.yaml cannot be found, please refer to the tutorial to confirm whether the configuration file exists"
        )

    # Check if configuration is read from API
    config = load_config()
    if config.get("read_config_from_api", False):
        print("Read configuration from API")
        old_config_origin = read_config(custom_config_file)
        if old_config_origin.get("selected_module") is not None:
            error_msg = "Your configuration file appears to contain both console and local configurations：\n"
            error_msg += "\nIt is recommended that you：\n"
            error_msg += "1、Copy the config_from_api.yaml file from the root directory to the data directory and rename it to .config.yaml\n"
            error_msg += "2、Configure the interface address and key according to the tutorial\n"
            raise ValueError(error_msg)
    config_file_valid = True
