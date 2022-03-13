from .word import Word


class Register:
    value = Word(0)
    max = 0

    def __init__(self, bit_size=16):
        self.value = Word(0)
        self.max = 2 ** bit_size - 1

    def validate(self, value):
        if value > self.max or value < 0:
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

    def add(self, value):
        value = Word(self.value + value)
        if not self.validate(value):
            raise TypeError("value %d exceeded the register limit", value)
        self.value = value

    # for future use
    def rotate(self, lr, al, count):
        bin_value = self.value.convert_to_binary()
        count_int = Word.from_bin_string(count)
        if lr == "0":
            new_binary_value = format((self.value << count_int), "016b")
            new_binary_value = new_binary_value[len(new_binary_value) - 16:16 - count_int] + \
                format(0, "016b")[0:count_int - len(new_binary_value) + 16] + \
                new_binary_value[0:len(new_binary_value) - 16]
            self.set(Word.from_bin_string(new_binary_value))
        else:
            new_binary_value = Word(self.value >> count_int).convert_to_binary()
            new_binary_value = bin_value[16 - count_int:16] + new_binary_value[count_int:16]
            self.set(Word.from_bin_string(new_binary_value))

    # for future use
    def shift(self, lr, al, count):
        if lr == "0":
            self.set(Word(self.value << Word.from_bin_string(count)))
        else:
            self.set(Word(self.value >> Word.from_bin_string(count)))
