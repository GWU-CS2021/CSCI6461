import datetime
import logging

from memory import Memory


def main():
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
    # TODO
    # init gui
    # init machine
    # ready
    # Design the init of simulator.


if __name__ == '__main__':
    main()
