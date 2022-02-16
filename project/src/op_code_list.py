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

    JZ: Final = "10"
    JNE: Final = "11"
    JCC: Final = "12"
    JMA: Final = "13"
    JSR: Final = "14"
    RFS: Final = "15"
    SOB: Final = "16"
    JGE: Final = "17"

    DVD: Final = "21"
    TRR: Final = "22"
    AND: Final = "23"
    ORR: Final = "24"
    NOT: Final = "25"

    SRC: Final = "31"
    RRC: Final = "32"

    FADD: Final = "33"
    FSUB: Final = "34"
    VADD: Final = "35"
    VSUB: Final = "36"
    CNVRT: Final = "37"

    LDX: Final = "41"
    STX: Final = "42"

    LDFR: Final = "50"
    STFR: Final = "51"

    IN: Final = "61"
    OUT: Final = "62"
    CHK: Final = "63"

