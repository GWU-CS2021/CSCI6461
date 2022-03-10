from typing import Final


class OpCodeList:
    # TODO
    # Change to oct
    HLT: Final = "0x00"
    LDR: Final = "0x01"
    STR: Final = "0x02"
    LDA: Final = "0x03"
    AMR: Final = "0x04"
    SMR: Final = "0x05"
    AIR: Final = "0x06"
    SIR: Final = "0x07"

    JZ: Final = "0x10"
    JNE: Final = "0x11"
    JCC: Final = "0x12"
    JMA: Final = "0x13"
    JSR: Final = "0x14"
    RFS: Final = "0x15"
    SOB: Final = "0x16"
    JGE: Final = "0x17"

    MLT: Final = "0x20"
    DVD: Final = "0x21"
    TRR: Final = "0x22"
    AND: Final = "0x23"
    ORR: Final = "0x24"
    NOT: Final = "0x25"

    SRC: Final = "0x31"
    RRC: Final = "0x32"

    FADD: Final = "0x33"
    FSUB: Final = "0x34"
    VADD: Final = "0x35"
    VSUB: Final = "0x36"
    CNVRT: Final = "0x37"

    LDX: Final = "0x41"
    STX: Final = "0x42"

    LDFR: Final = "0x50"
    STFR: Final = "0x51"

    IN: Final = "0x61"
    OUT: Final = "0x62"
    CHK: Final = "0x63"

    # format as r,x,address,i
    Group1 = {
        "LDR": LDR,
        "STR": STR,
        "LDA": LDA,
        "JZ": JZ,
        "JNE": JNE,
        "JCC": JCC,
        "SOB": SOB,
        "JGE": JGE,
        "AMR": AMR,
        "SMR": SMR
    }
    # format as x,address,i
    Group2 = {
        "LDX": LDX,
        "STX": STX,
        "JMA": JMA,
        "JSR": JSR
    }
    # format as immediate
    Group3 = {"RFS": RFS}
    # format as r, immediate
    Group4 = {
        "AIR": AIR,
        "SIR": SIR
    }
    # format as rx, ry
    Group5 = {
        "MLT": MLT,
        "DVD": DVD,
        "TRR": TRR,
        "AND": AND,
        "ORR": ORR,
        "NOT": NOT
    }
    # format as r, count , L/R, A/L
    Group6 = {
        "SRC": SRC,
        "RRC": RRC
    }
    # format as r, deviceId
    Group7 = {
        "IN": IN,
        "OUT": OUT,
        "CHK": CHK
    }
    # format as fr, x, address, i
    Group8 = {
        "FADD": FADD,
        "FSUB": FSUB,
        "VADD": VADD,
        "VSUB": VSUB,
        "CNVRT": CNVRT,
        "LDFR": LDFR,
        "STFR": STFR
    }
