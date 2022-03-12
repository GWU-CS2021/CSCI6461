
import logging
from .register import Register
from .memory import Memory
from .mfr import *


class CPU:
    def __init__(self, memory=Memory(2048)):
        self.logger = logging.getLogger("cpu")
        self.output_log = logging.getLogger("output2")
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
        # 1 indicate the machine is in halt
        self.halt_signal = 0
        # indicate the machine is waiting for keyboard input
        # if input_signal is not -1, it means reg[input_signal] is waiting input
        self.input_signal = -1
        # using rum_mode =0 will continue to single step after input.
        # using run_mode =1 will continue to continues step after input.
        # using run_mode =-1 will not run after hitting keyboard
        self.run_mode = 0
        # cache_display =0 -> dec output cache
        # 16 -> hex output cache, 2->binary output cache
        self.cache_display = 2

    def run(self):
        self.halt_signal = 0
        self.logger.info("start run")
        while self.halt_signal == 0 and self.input_signal == -1:
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
        self.input_signal = -1
        self.memory.init_program()

    def run_single_cycle(self):
        self.logger.info("start single cycle")
        try:
            # self.output_log.info("abc")
            # self.output_log.info(chr(13))
            self.halt_signal = 0
            # MAR <- PC
            self.mar.set(self.pc.get())

            # MBR <- MEM[MAR]
            self.mbr.set(self.memory.load_facade(self.mar.get()))

            # IR <- MBR
            self.ir.set(self.mbr.get())

            # parse and run
            # Locate and fetch operand data
            # Execute the operation
            # Deposit Results
            self._get_func_by_op()()

            # pc + 1 when in normal phase
            # if self.halt_signal == 0 and self.input_signal == -1:
                # PC++
            #    self.pc.add(1)

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
        self.memory.store_facade(self.mar.get(), self.mbr.get())
        self.logger.info("put %s(%d) to %s(%d) using store" % ( self.mbr.get().convert_to_binary(),self.mbr.get(), self.mar.get().convert_to_binary(),self.mar.get()))

    def store_plus(self):
        self.memory.store_facade(self.mar.get(), self.mbr.get())
        self.logger.info("put %s(%d) to %s(%d) using st+" % (
        self.mbr.get().convert_to_binary(), self.mbr.get(), self.mar.get().convert_to_binary(), self.mar.get()))
        self.mar.add(1)

    def load(self):
        self.mbr.set(self.memory.load_facade(self.mar.get()))
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
                "CC": self.cc.get().convert_to_binary(),
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
            "61": self._in,
            "62": self._out,
            "10": self._jz,
            "11": self._jne,
            "12": self._jcc,
            "13": self._jma,
            "14": self._jsr,
            "15": self._rfs,
            "16": self._sob,
            "17": self._jge,
            "04": self._amr,
            "05": self._smr,
            "06": self._air,
            "07": self._sir,
            "31": self._src,
            "32": self._rrc,
            "20": self._mlt,
            "21": self._dvd,
            "22": self._trr,
            "23": self._and,
            "24": self._orr,
            "25": self._not,
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
            addr_result = self.memory.load_facade(addr_result)
        return Word(addr_result)

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
        self.gpr[int(r, 2)].set(self.memory.load_facade(effective_addr))
        self.pc.add(1)
        return

    def _str(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # TODO what cache policy should apply?
        self.logger.debug("str %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.memory.store_facade(effective_addr, self.gpr[int(r, 2)].get())
        self.pc.add(1)
        return

    # just save effective address to reg
    def _lda(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("lda %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.gpr[int(r, 2)].set(effective_addr)
        self.pc.add(1)
        return

    def _ldx(self):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # raise error for x=0
        if ix == "00":
            raise MemoryError("trying to ldx with ix == 00")
        self.logger.debug("ldx %s,%s[%s] %s:%s" % (ix, addr, i, "effective:", effective_addr))
        self.ixr[int(ix, 2)].set(self.memory.load_facade(effective_addr))
        self.pc.add(1)
        return

    def _stx(self):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_load_store_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        # TODO what cache policy should apply?
        if ix == "00":
            raise MemoryError("trying to stx with ix == 00")
        self.logger.debug("stx %s,%s[%s] %s:%s" % (ix, addr, i, "effective:", effective_addr))
        self.memory.store_facade(effective_addr, self.ixr[int(ix, 2)].get())
        self.pc.add(1)
        return

    # request input from device
    def _in(self):
        self.logger.debug("")
        r, dev = self.ir.get().parse_as_io_cmd()
        if dev == "00000":
            # request input from keyboard
            self.input_signal = int(r, 2)
        else:
            self.logger.debug("requesting input for unsupported device %s" %(dev))
            return
        # pc add at input complete
        return

    def keyboard_input_action(self, value):
        # ignore input if not requested
        if self.input_signal == -1:
            self.run_mode = -1
            self.logger.debug("trying to input %s as not being requested" %(value))
            return
        # set input to requested reg(use ord to transform to ascii
        self.gpr[self.input_signal].set(Word(ord(value)))
        # set input signal to default
        self.input_signal = -1
        # pc add one here(after successfully input
        self.pc.add(1)

    def _out(self):
        self.logger.debug("")
        r, dev = self.ir.get().parse_as_io_cmd()
        if dev == "00001":
            self.logger.debug("outputting %s from reg %s" % (chr(self.gpr[int(r, 2)].get()),r))
            self.output_log.info(chr(self.gpr[int(r, 2)].get()))
        else:
            self.logger.debug("requesting output to unsupported device %s" % (dev))
            return
        self.pc.add(1)
        return

    def _jz(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jz %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        if self.gpr[int(r, 2)].get() == 0:
            self.pc.set(effective_addr)
            self.logger.debug("jz jumpping to %s" % effective_addr)
        else:
            self.pc.add(1)
            self.logger.debug("jz no jump")
        return

    def _jne(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jne %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        if self.gpr[int(r, 2)].get() != 0:
            self.pc.set(effective_addr)
            self.logger.debug("jne jumpping to %s" % effective_addr)
        else:
            self.pc.add(1)
            self.logger.debug("jne no jump")
        return

    def _jcc(self):
        self.logger.debug("")
        cc, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jcc %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        if self.cc.get()[int(cc, 2)] != 0:
            self.pc.set(effective_addr)
            self.logger.debug("jcc jumpping to %s" % effective_addr)
        else:
            self.pc.add(1)
            self.logger.debug("jcc no jump")
        return

    def _jma(self):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jma %s,%s[%s] %s:%s" % ( ix, addr, i, "effective:", effective_addr))
        self.pc.set(effective_addr)
        return

    def _jsr(self):
        self.logger.debug("")
        _, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jsr %s,%s[%s] %s:%s" % ( ix, addr, i, "effective:", effective_addr))
        self.gpr[3].set(self.pc.get()+1)
        self.pc.set(effective_addr)
        return

    def _rfs(self):
        self.logger.debug("")
        _, _, _, immed = self.ir.get().parse_as_transfer_cmd()
        # effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("rfs immed: %s jump back to :%s" % (immed,self.gpr[3].get()))
        self.gpr[0].set(Word.from_bin_string(immed))
        self.pc.set(self.gpr[3].get())
        return

    def _sob(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("sob %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        self.gpr[int(r, 2)].add(-1)
        if self.gpr[int(r, 2)].get() > 0:
            self.pc.set(effective_addr)
            self.logger.debug("sob jumpping to %s" % effective_addr)
        else:
            # reg == 0
            self.pc.add(1)
            self.logger.debug("sob no jump")
        return

    def _jge(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_transfer_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("jge %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        if self.gpr[int(r, 2)].get() >= 0:
            self.pc.set(effective_addr)
            self.logger.debug("jge jumpping to %s" % effective_addr)
        else:
            self.pc.add(1)
            self.logger.debug("jge no jump")
        return

    def _amr(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_arith_logical_basic_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("amr %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        result = self.gpr[int(r, 2)].get()+self.memory.load_facade(effective_addr)
        if result > 65535:
            self.cc.set(Word.from_bin_string(cc_overflow))
        self.gpr[int(r, 2)].set(Word(result))
        self.pc.add(1)
        return

    def _smr(self):
        self.logger.debug("")
        r, ix, i, addr = self.ir.get().parse_as_arith_logical_basic_cmd()
        effective_addr = self._get_effective_address(ix, i, addr)
        self.logger.debug("smr %s,%s,%s[%s] %s:%s" % (r, ix, addr, i, "effective:", effective_addr))
        result = self.gpr[int(r, 2)].get()-self.memory.load_facade(effective_addr)
        if result < 0:
            self.cc.set(Word.from_bin_string(cc_underflow))
        self.gpr[int(r, 2)].set(Word(result))
        self.pc.add(1)
        return

    def _air(self):
        self.logger.debug("")
        r, _,_, immed = self.ir.get().parse_as_arith_logical_basic_cmd()
        self.logger.debug("air %s,%s" % (r,immed))
        result = self.gpr[int(r, 2)].get() + Word.from_bin_string(immed)
        if result > 65535:
            self.cc.set(Word.from_bin_string(cc_overflow))
        self.gpr[int(r, 2)].set(Word(result))
        self.pc.add(1)
        return

    def _sir(self):
        self.logger.debug("")
        r, _,_, immed = self.ir.get().parse_as_arith_logical_basic_cmd()
        self.logger.debug("sir %s,%s" % (r,immed))
        result = self.gpr[int(r, 2)].get() - Word.from_bin_string(immed)
        if result < 0:
            self.cc.set(Word.from_bin_string(cc_underflow))
        self.gpr[int(r, 2)].set(Word(result))
        self.pc.add(1)
        return

    # TODO add support for negative if needed
    def _src(self):
        r,lr,al,count = self.ir.get().parse_as_shift_rotate_cmd()
        self.logger.debug("src %s,%s,%s,%s" % (r,lr,al,count))
        self.gpr[int(r,2)].shift(lr,al,count)
        self.pc.add(1)

    def _rrc(self):
        r,lr,al,count = self.ir.get().parse_as_shift_rotate_cmd()
        self.logger.debug("rrc %s,%s,%s,%s" % (r,lr,al,count))
        self.gpr[int(r,2)].rotate(lr,al,count)
        self.pc.add(1)

    def _mlt(self):
        rx,ry = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("mlt %s,%s" %(rx,ry))
        if rx not in ["00","10"] or ry not in ["00","10"]:
            self.logger.error("rx or ry position not correct")
            return
        result = self.gpr[int(rx,2)].get() * self.gpr[int(ry,2)].get()
        self.gpr[int(rx, 2)+1].set(Word(result % (1<<16)))
        self.gpr[int(rx, 2)].set(Word(result >> 16))
        self.pc.add(1)

    def _dvd(self):
        rx, ry = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("dvd %s,%s" % (rx, ry))
        if rx not in ["00", "10"] or ry not in ["00", "10"]:
            self.logger.error("rx or ry position not correct")
            return
        if self.gpr[int(ry, 2)].get() == 0:
            self.cc.set(Word.from_bin_string(cc_divzero))
            return
        result = self.gpr[int(rx, 2)].get().convert_to_float() / self.gpr[int(ry, 2)].get().convert_to_float()
        self.gpr[int(rx, 2) + 1].set(Word(self.gpr[int(rx, 2)].get() % self.gpr[int(ry, 2)].get()))
        self.gpr[int(rx, 2)].set(Word(int(result)))
        self.pc.add(1)

    def _trr(self):
        rx, ry = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("trr %s,%s" % (rx, ry))
        result = "0"
        if self.gpr[int(rx, 2)].get() == self.gpr[int(ry, 2)].get():
            result = "1"
        c_string = self.cc.get().convert_to_binary()
        c_string[15] = result
        self.cc.set(c_string)
        self.pc.add(1)

    def _and(self):
        rx, ry = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("and %s,%s" % (rx, ry))
        self.gpr[int(rx, 2)].set(Word(self.gpr[int(rx, 2)].get() & self.gpr[int(ry, 2)].get()))
        self.pc.add(1)

    def _orr(self):
        rx, ry = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("orr %s,%s" % (rx, ry))
        self.gpr[int(rx, 2)].set(Word(self.gpr[int(rx, 2)].get() | self.gpr[int(ry, 2)].get()))
        self.pc.add(1)

    def _not(self):
        rx, _ = self.ir.get().parse_as_arith_logical_xy_cmd()
        self.logger.debug("not %s" % (rx))
        self.gpr[int(rx, 2)].set(Word(self.gpr[int(rx, 2)].get() ^ 65535))
        self.pc.add(1)