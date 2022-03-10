import logging
from op_code_list import OpCodeList

class Assemble:

    def assemble(self, file_path="instruction.txt"):
        # print(format(int(OpCodeList.JGE, 16), "b"))
        logging.info("Assemble start working.")
        binary_instruction_list = []
        with open(file_path) as instruction_reader:
            for line in instruction_reader:
                line = line.strip("\n")
                line = self.convert_instruction_to_binary(line)
                binary_instruction_list.append(line)
        logging.info("Assemble ends.")
        return binary_instruction_list

    def convert_instruction_to_binary(self, data_list):
        data_list = self.preprocess(data_list)
        binary_string = ""
        instruction = data_list[0]
        print(data_list)
        if instruction == "HLT":
            binary_string += "0000000000000000"
        if instruction == "TRAP":
            binary_string += "1100000000000000"
        # format as r,x,address,i
        if instruction in OpCodeList.Group1:
            binary_string += format(int(OpCodeList.Group1[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += format(int(data_list[2]), "02b")
            if len(data_list) >= 5:
                binary_string += format(int(data_list[4]), "01b")
            else:
                binary_string += "0"
            binary_string += format(int(data_list[3]), "05b")
        # format as x,address,i
        elif instruction in OpCodeList.Group2:
            binary_string += format(int(OpCodeList.Group2[instruction], 16), "06b")
            binary_string += "00"
            binary_string += format(int(data_list[1]), "02b")
            if len(data_list) >= 4:
                binary_string += format(int(data_list[3]), "01b")
            else:
                binary_string += "0"
            binary_string += format(int(data_list[2]), "05b")
        # format as immediate
        elif instruction in OpCodeList.Group3:
            binary_string += format(int(OpCodeList.Group3[instruction], 16), "06b")
            binary_string += "00000"
            binary_string += format(int(data_list[1]), "05b")
        # format as r, immediate
        elif instruction in OpCodeList.Group4:
            binary_string += format(int(OpCodeList.Group4[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += "000"
            binary_string += format(int(data_list[2]), "05b")
        # format as rx, ry
        elif instruction in OpCodeList.Group5:
            binary_string += format(int(OpCodeList.Group5[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += format(int(data_list[2]), "02b")
            binary_string += "000000"
        # format as r, count , L/R, A/L
        elif instruction in OpCodeList.Group6:
            binary_string += format(int(OpCodeList.Group6[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += format(int(data_list[4]), "01b")
            binary_string += format(int(data_list[3]), "01b")
            binary_string += "0"
            binary_string += format(int(data_list[2]), "05b")
        # format as r, deviceId
        elif instruction in OpCodeList.Group7:
            binary_string += format(int(OpCodeList.Group7[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += "000"
            binary_string += format(int(data_list[2]), "05b")
        # format as fr, x, address, i
        elif instruction in OpCodeList.Group8:
            binary_string += format(int(OpCodeList.Group8[instruction], 16), "06b")
            binary_string += format(int(data_list[1]), "02b")
            binary_string += format(int(data_list[2]), "02b")
            if len(data_list) >= 5:
                binary_string += format(int(data_list[4]), "01b")
            else:
                binary_string += "0"
            binary_string += format(int(data_list[3]), "05b")
        return binary_string

    def preprocess(self, data):
        data_list = []
        start = 0
        for index in range(len(data)):
            if (data[index] == ' ') or (data[index] == ','):
                data_list.append(data[start:index])
                start = index + 1
            if index == len(data) - 1:
                data_list.append(data[start:index + 1])
        data_list[0] = data_list[0].upper()
        return data_list

def main():
    test = Assemble()
    print(test.assemble())

if __name__ == "__main__":
    main()