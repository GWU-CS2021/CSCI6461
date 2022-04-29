import datetime
from .mfr import *
from .word import Word
from .cache import CacheLine
import logging

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
        self.memory = [Word(0) for _ in range(size)]
        self.size = size
        self.logger = logging.getLogger("cpu")
        # lookup by address
        self.cache = [CacheLine() for _ in range(16)]
        # malloc location
        self.cache_map = {}
        # used to show cache hit in frontend
        self.cache_update_at = -1
        # used to show cache update in frontend
        self.cache_hit_at = -1
        # used to show cache replacement in frontend
        self.cache_replace_at = -1
        # map address->cache location

    def _malloc_cache_index(self):
        index = 0
        oldest_timestamp = datetime.datetime.now()
        available_index = -1
        needpop = 1
        for cache_line in self.cache:
            if cache_line.addr == Word(0):
                # already malloc
                available_index = index
                needpop = 0
                break
            if cache_line.last_update < oldest_timestamp:
                oldest_timestamp = cache_line.last_update
                available_index = index
            index += 1
        if needpop:
            # remove old entry
            self.cache_map.pop(self.cache[available_index].addr, None)
        return available_index

    def store_facade(self, address, value):
        # store to memory
        self._store(address, value)
        # check if in cache
        if address in self.cache_map:
            # update cache
            self.logger.debug("updating cache of address %d to value %d" % (address, value))
            self.cache[self.cache_map[address]] = CacheLine(Word(address), Word(value), datetime.datetime.now())
            self.cache_update_at = self.cache_map[address]
            # self.cache_hit_at = -1
            # self.cache_replace_at = -1
        else:
            # malloc location
            index = self._malloc_cache_index()
            self.logger.debug("replacing cache of address %d to address %d" % (self.cache[index].addr, address))
            self.cache_map[address] = index
            self.cache[index] = CacheLine(Word(address), Word(value), datetime.datetime.now())
            # self.cache_hit_at = -1
            # self.cache_update_at = -1
            self.cache_replace_at = index

    def load_facade(self, address):
        if address not in self.cache_map:
            memory_value = self._load(address)
            # update cache
            index = self._malloc_cache_index()
            self.logger.debug("replacing cache of address %d to address %d" % (self.cache[index].addr, address))
            self.cache_map[address] = index
            self.cache[index] = CacheLine(Word(address), Word(memory_value), datetime.datetime.now())
            # self.cache_hit_at = -1
            # self.cache_update_at = -1
            self.cache_replace_at = index
        else:
            # cache hit, update access time
            self.cache[self.cache_map[address]].last_update = datetime.datetime.now()
            self.cache_hit_at = self.cache_map[address]
            # self.cache_update_at = -1
            # self.cache_replace_at = -1
            self.logger.debug("cache hit at address %d" % address)
        return self.cache[self.cache_map[address]].value

    def reset(self):
        self.memory = [Word(0) for _ in range(self.size)]
        self.cache = [CacheLine() for _ in range(16)]
        # malloc location
        self.cache_map = {}

        self.cache_update_at = -1
        self.cache_hit_at = -1
        self.cache_replace_at = -1

    def validate_addr(self, addr):
        if addr >= self.size or addr < memory_start:
            return False
        return True

    def validate_load_addr(self, addr):
        if addr >= self.size or addr < 0:
            return False
        return True

    def _store(self, address, value):
        if not isinstance(value, Word):
            raise TypeError("value must be set to Word type")
        if not isinstance(address, Word):
            raise TypeError("address must be set to Word type")
        if not self.validate_addr(address):
            raise MemOverflowErr("memory address %d overflow" % address)
        self.memory[address] = value

    def store_reserved(self, target, value):
        target_addr_map = {res_trap: 0, res_mfr: 1, res_trap_pc: 2, res_mfr_pc: 4}
        if target not in target_addr_map:
            raise MemoryError("reserved target %s doesn't exist", target)
        if not isinstance(value, Word):
            raise MemReserveErr("value must be set to Word type")
        self.memory[target_addr_map[target]] = value

    def _load(self, address):
        if not self.validate_load_addr(address):
            raise MemOverflowErr("memory address %d overflow" % address)
        self.logger.debug("loading address %d from memory, value %d" % (address, self.memory[address]))
        return self.memory[address]

    def init_program(self, file_path="IPL.txt"):
        start_addr = Word(0)
        with open(file_path) as program_reader:
            for line in program_reader:
                words = line.split("#")
                words = words[0].split("$")
                words = words[0].strip("\n")
                words = words.split(" ")

                if len(words) < 2:
                    self.logger.debug("skipped invalid line %s" % line)
                    continue
                if len(words[0]) != 4 or len(words[1]) != 4:
                    self.logger.debug("skipped invalid line %s,%s,%s" % (line, words[0], words[1]))
                    continue
                addr, value = Word.from_hex_string(words[0]), Word.from_hex_string(words[1])
                if start_addr == Word(0):
                    # save the first addr
                    start_addr = addr
                self.logger.debug("storing %d,%d" % (addr, value))
                self._store(addr, value)
        self.logger.info("Program loaded with start at %d" % start_addr)
        return start_addr
        # return the start of memory addr for pc usage

    def load_file(self, start, file_path="paragraph.txt"):
        self.logger.info("load file %s at %d" % (file_path, start))
        with open(file_path, "r+") as p_reader:
            tmp_string = p_reader.read()
            counter = start
            for char in tmp_string:
                asc_code = ord(char)
                if asc_code == 10:
                    asc_code = 13
                self._store(Word(counter), Word(asc_code))
                counter += 1
                if counter >= self.size:
                    raise MemOverflowErr
            start_loc, end_loc = Word(30), Word(31)
            self._store(start_loc, Word(start))
            self._store(end_loc, Word(counter))
        self.logger.info("load finished, start %d, end %d" % (start, counter))

