# Word, basic datastructures of the simulator, check value length here, check upon assignment to register.

class Word(int):
    value = 0

    def __init__(self, value):
        self.max = 2 ** 16 - 1
        if not isinstance(value, int):
            raise TypeError("word must be set to an integer")
        if not self.validate(value):
            raise TypeError("value %d exceeded the word limit", value)
        self.value = value

    @staticmethod
    def from_bin_string(value):
        return Word(int(value, 2))

    @staticmethod
    def from_oct_string(value):
        return Word(int(value, 8))

    @staticmethod
    def from_hex_string(value):
        return Word(int(value, 16))

    def convert_to_binary(self):
        return format(self.value, "016b")

    def convert_to_hex(self):
        return format(self.value, "04x")

    # TODO implement in part IV
    def convert_to_float(self):
        return float(self.value)

    def validate(self, value):
        if value > self.max:
            return False
        return True

    def get_op_code(self):
        return self.convert_to_binary()[0:6]

    # commands below starting with parse will return the elements of the specific command in binary string form
    # for opcode_8 in [30]
    def parse_as_trap_cmd(self):
        trap_code = self.convert_to_binary()[12:16]
        return trap_code

    # for opcode_8 in [01,02,03,41,42]
    def parse_as_load_store_cmd(self):
        binary_word = self.convert_to_binary()
        r, ix, i, addr = binary_word[6:8], binary_word[8:10], binary_word[10:11], binary_word[11:16]
        return r, ix, i, addr

    # for opcode_8 in [10,11,12,13,14,15,16,17]
    def parse_as_transfer_cmd(self):
        # same structure as load/store, reserved for further implementation
        binary_word = self.convert_to_binary()
        r, ix, i, addr = binary_word[6:8], binary_word[8:10], binary_word[10:11], binary_word[11:16]
        return r, ix, i, addr

    # for opcode_8 in [04,05,06,07]
    def parse_as_arith_logical_basic_cmd(self):
        # same structure as load/store, reserved for further implementation
        binary_word = self.convert_to_binary()
        r, ix, i, addr = binary_word[6:8], binary_word[8:10], binary_word[10:11], binary_word[11:16]
        return r, ix, i, addr

    # for opcode_8 in [20,21,22,23,24,25]
    def parse_as_arith_logical_xy_cmd(self):
        binary_word = self.convert_to_binary()
        rx, ry = binary_word[6:8], binary_word[8:10]
        return rx, ry

    # for opcode_8 in [31,32]
    def parse_as_shift_rotate_cmd(self):
        binary_word = self.convert_to_binary()
        r, al, lr, count = binary_word[6:8], binary_word[8], binary_word[9], binary_word[12:16]
        return r, al, lr, count

    # for opcode_8 in [61,62,63]
    def parse_as_io_cmd(self):
        binary_word = self.convert_to_binary()
        r, dev_id = binary_word[6:8], binary_word[11:16]
        return r, dev_id

    # for opcode_8 in [33,34,35,36,37,50,51]
    def parse_as_float_cmd(self):
        binary_word = self.convert_to_binary()
        fr, i, ix, addr = binary_word[6:8], binary_word[8], binary_word[9:11], binary_word[11:16]
        return fr, i, ix, addr
