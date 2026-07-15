import logging.config
import json

def setup_logging():
    with open("logging.json", "r") as f:
        config = json.load(f)
    logging.config.dictConfig(config)

 
def get_logger(module_name:str)-> logging.Logger:
    return logging.getLogger(module_name)
