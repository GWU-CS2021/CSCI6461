# TODO
# Design CPU architecture for phase 1.
import logging

from register import Register
from word import Word
from memory import Memory
from mfr import *


class CPU:
    def __init__(self, memory=Memory(2048)):
        self.logger = logging.getLogger("root")
        self.memory = memory
        self.pc = Register(pc_max)
        self.mar = Register(mar_max)
        self.mbr = Register(mbr_max)
        self.gpr = [Register(reg_size) for i in range(0, 4)]
        # although 4 ixr is assigned, the first ixr will always be 0 to avoid conflicts in code.
        self.ixr = [Register(reg_size) for i in range(0, 4)]
        self.cc = Register(cc_max)
        self.mfr = Register(mfr_max)
        self.ir = Register(ir_max)
        self.halt_signal = 0

    def run(self):
        self.halt_signal = 0
        self.logger.info("start run")
        while self.halt_signal == 0:
            self.run_single_cycle()

    def init_program(self):
        self.memory.reset()
        self.pc.reset()
        self.mar.reset()
        self.mbr.reset()
        for gpr in self.gpr:
            gpr.reset()
        for ixr in self.ixr:
            ixr.reset()
        self.cc.reset()
        self.mfr.reset()
        self.ir.reset()
        self.halt_signal = 0
        self.memory.init_program()

    # TODO this part will be refactored when implementing pipeline
    def run_single_cycle(self):
        self.logger.info("start single cycle")
        try:
            self.halt_signal = 0
            # MAR <- PC
            self.mar.set(self.pc.get())

            # MBR <- MEM[MAR]
            self.mbr.set(self.memory.memory[self.mar.get()])

            # IR <- MBR
            self.ir.set(self.mbr.get())

            # parse and run
            # Locate and fetch operand data
            # Execute the operation
            # Deposit Results
            self._get_func_by_op()()

            if self.halt_signal != 1:
                # PC++
                self.pc.add(1)

            # exit on halt


        # TODO mfr will be implemented in phase3
        except MemReserveErr as e:
            self.logger.error("MemReserveErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_mem_reserve]
            return
        except TrapErr as e:
            self.logger.error("TrapErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_trap]
            return
        except OpCodeErr as e:
            self.logger.error("OpCodeErr %s" % (e))
            self.halt_signal = 1
            # self.mfr = mapping_mfr_value[mfr_op_code]
            return
        except MemOverflowErr as e:
            self.halt_signal = 1
            self.logger.error("MemOverflowErr %s" % (e))
            # self.mfr = mapping_mfr_value[mfr_mem_overflow]
            return
        except Exception as e:
            self.logger.error(e)
            return

    def store(self):
        self.memory.store(self.mar.get(), self.mbr.get())
        self.logger.info("put %s(%d) to %s(%d) using store" % ( self.mbr.get().convert_to_binary(),self.mbr.get(), self.mar.get().convert_to_binary(),self.mar.get()))

    def store_plus(self):
        self.memory.store(self.mar.get(), self.mbr.get())
        self.logger.info("put %s(%d) to %s(%d) using st+" % (
        self.mbr.get().convert_to_binary(), self.mbr.get(), self.mar.get().convert_to_binary(), self.mar.get()))
        self.mar.add(1)

    def load(self):
        self.mbr.set(self.memory.load(self.mar.get()))
        self.logger.info("load memory[%s(%d)] to mbr[%s(%d)] using load" % (
        self.mar.get().convert_to_binary(), self.mar.get(), self.mbr.get().convert_to_binary(), self.mbr.get()))

    def get_all_reg(self):
        return {"PC": self.pc.get().convert_to_binary(),
                "MAR": self.mar.get().convert_to_binary(),
                "MBR": self.mbr.get().convert_to_binary(),
                "GPR0": self.gpr[0].get().convert_to_binary(),
                "GPR1": self.gpr[1].get().convert_to_binary(),
                "GPR2": self.gpr[2].get().convert_to_binary(),
                "GPR3": self.gpr[3].get().convert_to_binary(),
                "IXR1": self.ixr[1].get().convert_to_binary(),
                "IXR2": self.ixr[2].get().convert_to_binary(),
                "IXR3": self.ixr[3].get().convert_to_binary(),
                "cc": self.cc.get().convert_to_binary(),
                "MFR": self.mfr.get().convert_to_binary(),
                "IR": self.ir.get().convert_to_binary(),
                }

    def _get_func_by_op(self):
        op = self.ir.get().get_op_code()
        # opcode from binary string to oct string
        op_oct = format(int(op, 2), "02o")
        mapping_op_function = {
            "00": self._hlt,
            "01": self._ldr,
            "02": self._str,
            "03": self._lda,
            "41": self._ldx,
            "42": self._stx,
        }
        #opcode from binary string to oct string
        op_oct = format(int(op,2), "02o")
        if op_oct not in mapping_op_function:
            raise OpCodeErr("illegal opcode %s" % op_oct)
        return mapping_op_function[op_oct]

    # ix,i,addr input should all be binary string here
    def _get_effective_address(self, ix, i, addr):
        self.logger.debug("paring effective address,ix %s, i %s, addr %s"%(ix,i,addr))
        ix_int = int(ix, 2)
        addr_result = int(addr, 2)
        # addr_result = self.memory.load(Word(addr_int))
        if ix_int > 0:
            addr_result = Word(addr_result + self.ixr[ix_int].get())
        if i == "1":
            addr_result = self.memory.load(addr_result)
        return addr_result

    # functions below is to match each and every opcode
    # Should we put all the instruction code separately here?
    # Or we can use switch case to declare different scene.
    # halt
    def _hlt(self):
        self.logger.debug("")
        self.halt_signal = 1
        return

    # LOAD/STORE
    def _ldr(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # TODO what cache policy should apply?
        self.logger.debug("ldr %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.gpr[int(r, 2)].set(self.memory.load(effective_addr))
        return

    def _str(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # TODO what cache policy should apply?
        self.logger.debug("str %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.memory.store(effective_addr, self.gpr[int(r, 2)].get())
        return

    # just save effective address to reg
    def _lda(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("lda %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.gpr[int(r, 2)].set(effective_addr)
        return

    def _ldx(self):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # raise error for x=0
        if ix == "00":
            raise MemoryError("trying to ldx with ix == 00")
        self.logger.debug("ldx %s,%s[%s] %s:%s" % (ix, addr, i, "effective:", effective_addr))
        self.ixr[int(ix, 2)].set(self.memory.load(effective_addr))
        return

    def _stx(self, code):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # TODO what cache policy should apply?
        if ix == "00":
            raise MemoryError("trying to stx with ix == 00")
        self.logger.debug("stx %s,%s[%s] %s:%s" % (ix, addr, i, "effective:", effective_addr))
        self.memory.store(effective_addr, self.ixr[int(ix, 2)].get())
        return