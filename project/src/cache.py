# cache hit -> read, renew counter
# cache miss -> read from memory and write cache
# cache update(upon memory update) -> renew
# cache write(upon store to memory) -> write to cache
# cache full -> kick LRU line