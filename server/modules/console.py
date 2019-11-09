import datetime
from colorama import init
from termcolor import colored
init()

class console_base:
    @staticmethod
    def time_now(formatting: str = "%m.%d.%Y || %H:%M:%S"):
        return datetime.datetime.now().strftime(formatting)

    @staticmethod
    def Error(error: str):
        print(colored(f"ERROR {console_base.time_now()}: {error}", 'red'))

    @staticmethod
    def Warning(warn: str):
        print(colored(f"WARNING {console_base.time_now()}: {warn}", 'yellow'))

    @staticmethod
    def Success(text: str):
        print(colored(f"SUCCESS {console_base.time_now()}: {text}", 'green'))