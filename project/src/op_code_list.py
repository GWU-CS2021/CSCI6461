from typing import Final


class OpCodeList:
    # TODO
    # Change to oct
    HLT: Final = "00"
    LDR: Final = "01"
    STR: Final = "02"
    LDA: Final = "03"
    AMR: Final = "04"
    SMR: Final = "05"
    AIR: Final = "06"
    SIR: Final = "07"

    JZ: Final = "010"
    JNE: Final = "011"
    JCC: Final = "012"
    JMA: Final = "013"
    JSR: Final = "014"
    RFS: Final = "015"
    SOB: Final = "016"
    JGE: Final = "017"

    MLT: Final = "020"
    DVD: Final = "021"
    TRR: Final = "022"
    AND: Final = "023"
    ORR: Final = "024"
    NOT: Final = "025"

    SRC: Final = "031"
    RRC: Final = "032"

    FADD: Final = "033"
    FSUB: Final = "034"
    VADD: Final = "035"
    VSUB: Final = "036"
    CNVRT: Final = "037"

    LDX: Final = "041"
    STX: Final = "042"

    LDFR: Final = "050"
    STFR: Final = "051"

    IN: Final = "061"
    OUT: Final = "062"
    CHK: Final = "063"

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
