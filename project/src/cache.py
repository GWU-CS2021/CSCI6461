# cache hit -> read, renew counter
# cache miss -> read from memory and write cache
# cache update(upon memory update) -> renew
# cache write(upon store to memory) -> write to cache
# cache full -> kick LRU line
# read through cache
# write through cache
# fifo
import datetime

from .word import Word


class CacheLine:
    def __init__(self,addr=Word(0),value=Word(0),last_update=datetime.datetime.now()):
        self.addr = addr
        self.value = value
        self.last_update = last_update

