from word import Word


class Memory:
    memory = [Word(0) for i in range(2048)]
    length = 2048

    def __init__(self):
        # Need to be expandable to 4096 words
        self.memory = [Word(0) for i in range(2048)]

    @staticmethod
    def validate(value):
        if value > 2048:
            return False
        return True

# TODO
# How to design the methods for store and load.

    def store(self, address, value):
        if not isinstance(value, Word):
            raise TypeError("value must be set to Word type")
        if not isinstance(address, Word):
            raise TypeError("address must be set to Word type")
        if not self.validate(address):
            raise TypeError("memory address %d overflow", address)
        self.memory[address] = value

    def load(self, address):
        if not self.validate(address):
            raise TypeError("memory address %d overflow", address)
        return self.memory[address]
