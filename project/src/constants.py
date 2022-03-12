# This file is an interface to declare CPU constants such as
# DEFAULT_BIT_SIZE...
# R0-R3, X1-X3...
from .word import Word
# TODO
# General CPU constants

# Public constants for register names

memory_size = 12
bit_size = 16
pc_max = memory_size
cc_max = 4
ir_max = bit_size
mar_max = memory_size
mbr_max = bit_size
mfr_max = 4
reg_size = bit_size

# 0	Illegal Memory Address to Reserved Locations
mfr_mem_reserve = "reserve"
# 1	Illegal TRAP code
mfr_trap = "trap"
# 2	Illegal Operation Code
mfr_op_code = "op_code"
# 3	Illegal Memory Address beyond 2048 (memory installed)
mfr_mem_overflow = "overflow"

cc_overflow = "1000"
cc_underflow = "0100"
cc_divzero = "0010"
cc_equalornot = "0001"

mapping_mfr_value = {
    mfr_mem_reserve: Word(1),
    mfr_trap: Word(2),
    mfr_op_code: Word(4),
    mfr_mem_overflow: Word(8)
}

