from word import Word


class Register:

    def __init__(self, bit_size=16):
        self.value = Word(0)
        self.max = 2 ** bit_size

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


'''
    def get(self):
        return self.value

    def reset(self):
        self.value = Word(0)
'''
