import configparser

config_parser = configparser.ConfigParser()
config_parser.read("./test/config.cfg")

tests_config = config_parser["TEST"]
