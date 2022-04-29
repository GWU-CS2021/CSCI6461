# cache hit -> read, renew counter
# cache miss -> read from memory and write cache
# cache update(upon memory update) -> renew
# cache write(upon store to memory) -> write to cache
# cache full -> kick LRU line
# read through cache
# write through cache
# fifo
import datetime
import logging

from .mfr import OpCodeErr
from .word import Word





class CacheLine:
    def __init__(self, addr=Word(0), value=Word(0), last_update=datetime.datetime.now()):
        self.addr = addr
        self.value = value
        self.last_update = last_update


class ROBLine:
    def __init__(self,command="",status=""):
        self.command = command
        self.status = status


# ROB 1: populate with following command, 2: able to commited/reverted all command
class ROB:
    def __init__(self):
        self.buffer = [ROBLine() for _ in range(8)]
        self.logger = logging.getLogger("cpu")

    def reset(self):
        self.buffer = [ROBLine() for _ in range(8)]

    def populate(self, pc ,memory):
        self.reset()
        index = 0
        while index < 8:
            curr_ir = memory[pc+index]
            command = self._get_name_by_op(curr_ir)
            if command in ["jz", "jne", "jcc", "sob", "jge"]:
                break
            self.buffer[index] = ROBLine(command, "")
            if command == "hlt":
                break
            index += 1

    def change_status(self,status=""):
        for rob in self.buffer:
            if rob.command == "":
                break
            rob.status = status

    def _get_name_by_op(self,command):
        # opcode from binary string to oct string
        # op_oct = format(int(op, 2), "02o")
        mapping_op_function = {
            "00": "hlt",
            "01": "ldr",
            "02": "str",
            "03": "lda",
            "41": "ldx",
            "42": "stx",
            "61": "in",
            "62": "out",
            "63": "chk",
            "10": "jz",
            "11": "jne",
            "12": "jcc",
            "13": "jma",
            "14": "jsr",
            "15": "rfs",
            "16": "sob",
            "17": "jge",
            "04": "amr",
            "05": "smr",
            "06": "air",
            "07": "sir",
            "30": "trap",
            "31": "src",
            "32": "rrc",
            "20": "mlt",
            "21": "dvd",
            "22": "trr",
            "23": "and",
            "24": "orr",
            "25": "not",
        }
        # opcode from binary string to oct string
        op_oct = format(int(command.get_op_code(), 2), "02o")
        if op_oct not in mapping_op_function:
            self.logger.debug("illegal opcode %s" % op_oct)
            raise OpCodeErr("illegal opcode %s" % op_oct)
        return mapping_op_function[op_oct]


class BPBLine:
    def __init__(self, addr=Word(0), value=0, last_update=datetime.datetime.now()):
        self.addr = addr
        self.value = value
        self.last_update = last_update


# BPB 1: populate/update at every branch action, 2: bpb facade to get net pc for ROB to populate
class BPB:
    def __init__(self):
        self.map = {}
        self.buffer = [BPBLine() for _ in range(16)]
        self.logger = logging.getLogger("cpu")
        self.rob = ROB()
        self.cache_update_at = -1
        # used to show cache update in frontend
        self.cache_hit_at = -1
        # used to show cache replacement in frontend
        self.cache_replace_at = -1
        # map address->cache location

    def reset(self):
        self.map = {}
        self.buffer = [BPBLine() for _ in range(16)]
        self.rob.reset()
        self.cache_update_at = -1
        # used to show cache update in frontend
        self.cache_hit_at = -1
        # used to show cache replacement in frontend
        self.cache_replace_at = -1
        # map address->cache location

    def predict(self,pc,jump_pc,memory):
        if pc not in self.map:
            # update cache
            index = self._malloc_cache_index()
            self.logger.debug("replacing bpb of address %d to address %d" % (self.buffer[index].addr, pc))
            self.map[pc] = index
            self.buffer[index] = BPBLine(Word(pc), 0 , datetime.datetime.now())
            # self.cache_hit_at = -1
            # self.cache_update_at = -1
            self.cache_replace_at = index
        else:
            # cache hit, update access time
            self.buffer[self.map[pc]].last_update = datetime.datetime.now()
            self.cache_hit_at = self.map[pc]
            self.logger.debug("bpb hit at address %d" % pc)
        # Populate ROB here
        if self.buffer[self.map[pc]].value == 1:
            jump_pc = Word(pc+1)
        self.rob.populate(jump_pc,memory)
        return self.buffer[self.map[pc]].value

    def validate(self,pc=Word(0),taken=0):
        if self.buffer[self.map[pc]].value != taken:
            self.buffer[self.map[pc]].value = taken
            self.buffer[self.map[pc]].last_update = datetime.datetime.now()
            self.rob.change_status("reverted")
            self.cache_update_at = self.map[pc]
            # revert ROB here
        else:
            self.rob.change_status("committed")
            self.buffer[self.map[pc]].last_update = datetime.datetime.now()
            #self.cache_hit_at = self.map[pc]
            # commit ROB here

    def _malloc_cache_index(self):
        index = 0
        oldest_timestamp = datetime.datetime.now()
        available_index = -1
        needpop = 1
        for cache_line in self.buffer:
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
            self.map.pop(self.buffer[available_index].addr, None)
        return available_index



# facade:
    # get predicted pc from BPB, populate rob
# update:
    # if new: add record, if record ==1 revert rob, else commit rob
    # if exist: if update != record, revert rob, else commit rob