import json
import os

import discord


class Config:
    def __init__(self):
        with open("environment.json") as config_file:
            self.data = json.load(config_file)

    @staticmethod
    def get(value, default=None):
        config_class = Config()
        if value not in config_class.data:
            if default is None:
                raise KeyError(f"{value} is not found and a default was not set")
            return default
        return config_class.data[value]

    @staticmethod
    def load_extensions(bot: discord.Bot, base_folder="modules", exclude=None):
        exclude = exclude or []
        for root, _, files in os.walk(base_folder):
            for file in files:
                if file.endswith(".py") and not file.startswith("__"):
                    # Get relative module path: e.g. modules.birthdays.commands -> "modules.birthdays.commands"
                    rel_path = os.path.relpath(os.path.join(root, file), ".").replace(os.sep, ".")
                    module_name = rel_path[:-3]  # remove ".py"
                    if file in exclude or module_name in exclude:
                        continue
                    try:
                        bot.load_extension(module_name)
                        print(f"Loaded extension: {module_name}")
                    except Exception as e:
                        print(f"Failed to load {module_name}: {e}")