from CSCI6461.project.utils.isa_decode import *


# TODO change this to unit test
def main():
    testvar = Word(10)
    print(testvar, testvar.binary())
    test_pc = Register(pc_max)
    test_pc.set(Word(99))
    print(test_pc.get().binary())
    m = Memory()
    m.store(Word(20), Word(4095))
    print(m.load(20))


if __name__ == '__main__':
    main()