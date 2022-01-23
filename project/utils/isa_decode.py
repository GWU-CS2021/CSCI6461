memory_size = 12
bit_size = 16
pc_max = memory_size
cc_max = 4
ir_max = bit_size
mar_max = memory_size
mbr_max = bit_size
mfr_max = 4
reg_size = bit_size


# Word, basic datastructures of the simulator, check value length here, check upon assignment to register
class Word(int):
    def __init__(self, value):
        self.max = 2 ** memory_size
        if not isinstance(value, int):
            raise TypeError("word must be set to an integer")
        if not self.validate(value):
            raise TypeError("value %d exceeded the register limit", value)
        self.value = value

    def binary(self):
        return format(self.value, "016b")

    def validate(self, value):
        if value > self.max:
            return False
        return True


class Register:
    def __init__(self, max_bit_size=bit_size):
        self.value = Word(0)
        self.max = 2 ** max_bit_size

    def validate(self, value):
        if value > self.max:
            return False
        return True

    def set(self, value):
        if not isinstance(value, Word):
            raise TypeError("value must be set to Word type")
        if not self.validate(value):
            raise TypeError("value %d exceeded the register limit", value)
        self.value = value

    def get(self):
        return self.value

    def reset(self):
        self.value = Word(0)


class Memory:
    def __init__(self):
        self.storage = [Word(0)for i in range(2 ** memory_size)]

    @staticmethod
    def validate(value):
        if value > 2 ** memory_size:
            return False
        return True

    def store(self, addr, value):
        if not isinstance(value, Word):
            raise TypeError("value must be set to Word type")
        if not isinstance(addr, Word):
            raise TypeError("address must be set to Word type")
        if not self.validate(addr):
            raise TypeError("memory address %d overflow", addr)
        self.storage[addr] = value

    def load(self, addr):
        if not self.validate(addr):
            raise TypeError("memory address %d overflow", addr)
        return self.storage[addr]


