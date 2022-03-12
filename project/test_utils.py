
import logging
import datetime
import src.cpu as cpu2
import src.register as reg
from src.word import Word

def set_log():
    loggers = logging.getLogger('root')
    loggers.setLevel(logging.DEBUG)

    # Create the Handler for logging data to a file
    logger_handler = logging.FileHandler(filename=datetime.datetime.now().strftime("%Y-%m-%d") + '.log')
    logger_handler.setLevel(logging.DEBUG)

    # Create a Formatter for formatting the log messages
    logger_formatter = logging.Formatter('[%(levelname)s:%(asctime)s - %(filename)s:%(lineno)s:%(funcName)10s() - ] - %(message)s')

    # Add the Formatter to the Handler
    logger_handler.setFormatter(logger_formatter)

    # Add the Handler to the Logger
    loggers.addHandler(logger_handler)

# TODO change this to unit test
def main():
    x = 128
    y = 127
    print (x | y)
    print (format(x,"016b"),format(x ^ 65535,"016b"))

if __name__ == '__main__':
    main()