# Configuration.py
import configparser
import os

def load_config(file_path):
    config = configparser.ConfigParser()
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Configuration file not found: {file_path}")

    config.read(file_path)

    return config

if __name__ == "__main__":
    config = load_config('data.cfg')
    print(config['SimulatedAnnealing'])
