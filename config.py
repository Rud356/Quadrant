import configparser

config_parser = configparser.ConfigParser()
config_parser.read("./config.cfg")

config = config_parser["SERVER"]
tests_config = config_parser["TEST"]
