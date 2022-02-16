from simulator.CSCI6461.project.src.word import *
from simulator.CSCI6461.project.src.register import *
from simulator.CSCI6461.project.src.constants import *
from simulator.CSCI6461.project.src.memory import *
from simulator.CSCI6461.project.src.cpu import CPU

import logging
import datetime

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
    set_log()
    # print(format(int("0000010100001100",2),"04x"))
    # print(format(int("0000010000001010", 2), "04x"))
    # loggers = logging.getLogger('root')
    # loggers.info("start")
    # testvar = Word(10)
    # print(testvar, testvar.convert_to_binary())
    # test_pc = Register(pc_max)
    # test_pc.set(Word(99))
    # print(test_pc.get().convert_to_binary())
    m = Memory(2048)
    cpu = CPU(m)
    # m.store(Word(20), Word(4095))
    # print(m.load(20))
    # print(Word(99).parse_as_float_cmd())
    # print(Word(99).get_op_code())
    # hex_val = '0009'
    # print(Word.from_hex_string(hex_val))

    program_start = m.init_program("IPL.txt")
    cpu.pc.set(program_start)
    # print(cpu.memory.load(32))
    print(cpu.get_all_reg())
    cpu.run_single_cycle()
    # print(format(int("1001",2), "02o"))

if __name__ == '__main__':
    main()