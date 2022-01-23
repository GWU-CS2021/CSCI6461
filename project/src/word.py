# Word, basic datastructures of the simulator, check value length here, check upon assignment to register
class Word(int):
    value = 0

    def __init__(self, value):
        self.max = 2 ** 16 - 1
        if not isinstance(value, int):
            raise TypeError("word must be set to an integer")
        if not self.validate(value):
            raise TypeError("value %d exceeded the register limit", value)
        self.value = value

    def convert_to_binary(self):
        return format(self.value, "016b")

    def validate(self, value):
        if value > self.max:
            return False
        return True
