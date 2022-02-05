import os
from .mfr import *
from .word import Word

# from constants import memory_size
memory_start = 8
# where to start load real data
# program_interval = 10
# res for reserved
res_trap = "trap"
res_mfr = "fault"
res_trap_pc = "trap_pc"
res_mfr_pc = "fault_pc"


class Memory:
    # memory = [Word(0) for i in range(2048)]
    # length = 2048

    def __init__(self, size=2048):
        # Need to be expandable to 4096 words
        self.memory = [Word(0) for i in range(size)]
        self.size = size

    def validate_addr(self, addr):
        if addr >= self.size or addr < memory_start:
            return False
        return True

    # TODO
    # How to design the methods for store and load.

    def store(self, address, value):
        if not isinstance(value, Word):
            raise TypeError("value must be set to Word type")
        if not isinstance(address, Word):
            raise TypeError("address must be set to Word type")
        if not self.validate_addr(address):
            raise MemOverflowErr("memory address %d overflow" % address)
        self.memory[address] = value

    def store_reserved(self, target, value):
        target_addr_map = {res_trap: 0, res_mfr: 1, res_trap_pc: 2, res_mfr_pc: 4}
        if not target in target_addr_map:
            raise MemoryError("reserved target %s doesn't exist", target)
        if not isinstance(value, Word):
            raise MemReserveErr("value must be set to Word type")
        self.memory[target_addr_map[target]]=value

    def load(self, address):
        if not self.validate_addr(address):
            raise MemOverflowErr("memory address %d overflow", address)
        return self.memory[address]

    def init_program(self, file_path="IPL.txt"):
        start_addr = Word(0)
        with open(file_path) as program_reader:
            for line in program_reader:
                words = line.split(" ")
                if len(words) != 2:
                    raise TypeError("invalid program line found,%s", line)
                addr, value = Word.from_hex_string(words[0]), Word.from_hex_string(words[1])
                if start_addr == Word(0):
                    # save the first addr
                    start_addr = addr
                self.store(addr, value)
        return start_addr
        # return the start of memory addr for pc usage
