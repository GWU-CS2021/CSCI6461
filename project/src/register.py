from .word import Word


class Register:
    def __init__(self, bit_size=16):
        self.value = Word(0)
        self.max = 2 ** bit_size - 1

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

# TODO
# Decide how to initialize register.
# Design methods for register.

    def get(self):
        return self.value

    def reset(self):
        self.value = Word(0)

    def add(self,value):
        value = Word(self.value+value)
        if not self.validate(value):
            raise TypeError("value %d exceeded the register limit", value)
        self.value = value

    # for future use
    def rotate(self,lr,al,count):
        pass

    # for future use
    def shift(self,lr,al,count):
        pass



