import configparser
import os

def load_config(path='config.ini'):
    config = configparser.ConfigParser()
    config.read(path, encoding='utf-8')
    return config

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True) 