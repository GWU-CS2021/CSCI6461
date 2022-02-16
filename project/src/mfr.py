from constants import *
import logging

loggers = logging.getLogger('root')


# ReserveLocationErr :0	Illegal Memory Address to Reserved Locations MFR set to binary 0001
class MemReserveErr(Exception):
    pass


# TrapCodeErr: 1 Illegal TRAP code  MFR set to binary 0010
class TrapErr(Exception):
    pass


# OpCodeErr:2	Illegal Operation Code MFR set to 0100
class OpCodeErr(Exception):
    pass


# OverflowErr:3	Illegal Memory Address beyond 2048 (memory installed)
class MemOverflowErr(Exception):
    pass
