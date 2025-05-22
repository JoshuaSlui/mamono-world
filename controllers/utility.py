import json


class Config:
    def __init__(self):
        with open('environment.json') as config_file:
            self.data = json.load(config_file)

    @staticmethod
    def get(value, default = None):
        config_class = Config()
        if value not in config_class.data:
            if default is None:
                raise KeyError(f'{value} is not found and a default was not set')
            return default
        return config_class.data[value]