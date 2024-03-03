import re
from dictionaries import * #importing dictionaries from dictionaries.py to avoid cluttering of code




# Define a function to convert a decimal number to a binary string with specified width
def bin(dec_num, width):
    return format(dec_num, '0' + str(width) + 'b')




#Functions to assemble all types of instructions (R, I, S, B, U, J)
def assemble_r_type(instruction, rd, rs1, rs2):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    funct7 = "0000000"  # Default value for R-type
    return funct7 + bin(rs2, 5) + bin(rs1, 5) + funct3 + bin(rd, 5) + opcode


def assemble_i_type(instruction, rd, rs1, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    return bin(imm, 12) + bin(rs1, 5) + funct3 + bin(rd, 5) + opcode


def assemble_s_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_11_5 = bin(imm >> 5, 7)
    imm_4_0 = bin(imm & 0x1F, 5)
    return imm_11_5 + bin(rs2, 5) + bin(rs1, 5) + funct3 + imm_4_0 + opcode


def assemble_b_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_12 = bin((imm >> 12) & 1, 1)
    imm_10_5 = bin((imm >> 5) & 0x3F, 6)
    imm_4_1 = bin((imm >> 1) & 0xF, 4)
    imm_11 = bin((imm >> 11) & 1, 1)
    return imm_12 + imm_10_5 + bin(rs2, 5) + bin(rs1, 5) + funct3 + imm_4_1 + imm_11 + opcode


def assemble_u_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    return bin(imm, 20) + bin(rd, 5) + opcode


def assemble_j_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    imm_20 = bin((imm >> 20) & 1, 1)
    imm_10_1 = bin((imm >> 1) & 0x3FF, 10)
    imm_11 = bin((imm >> 11) & 1, 1)
    imm_19_12 = bin((imm >> 12) & 0xFF, 8)
    return imm_20 + imm_10_1 + imm_11 + imm_19_12 + bin(rd, 5) + opcode








#Functions to parse assembly instructions and assemble them
def parse_instruction(line):
    line = line.strip()
    tokens = re.split(r'[,\s]+', line)
    instruction = tokens[0]
    operands = tokens[1:]
    return instruction, operands


def assemble_instruction(instruction, operands, symbol_table):
    if instruction not in instructions_Dictionary:
        return None  # Invalid instruction

    if not all(op in registers_Dictionary for op in operands):
        return None  # Invalid register name

    if instruction in ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and",
                       "mul", "rst", "halt", "rvrs", "div", "rem"]:  
        if len(operands) != 3:
            return None  # Incorrect number of operands
        rd, rs1, rs2 = map(int, operands)
        return assemble_r_type(instruction, rd, rs1, rs2)

    elif instruction in ["lw", "addi", "sltiu", "jalr"]:
        if len(operands) != 3:
            return None  # Incorrect number of operands
        rd, rs1 = map(int, operands[:2])
        imm = int(operands[2])
        if abs(imm) >= 2**12:
            return None  # Illegal immediate value
        return assemble_i_type(instruction, rd, rs1, imm)

    elif instruction == "sw":
        if len(operands) != 3:
            return None  # Incorrect number of operands
        rs1, rs2 = map(int, operands[:2])
        imm = int(operands[2])
        if abs(imm) >= 2**12:
            return None  # Illegal immediate value
        return assemble_s_type(instruction, rs1, rs2, imm)

    elif instruction in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
        if len(operands) != 3:
            return None  # Incorrect number of operands
        rs1, rs2 = map(int, operands[:2])
        label = operands[2]
        imm = symbol_table[label] - len(symbol_table)
        if abs(imm) >= 2**12:
            return None  # Illegal immediate value
        return assemble_b_type(instruction, rs1, rs2, imm)

    elif instruction in ["lui", "auipc"]:
        if len(operands) != 2:
            return None  # Incorrect number of operands
        rd = int(operands[0])
        imm = int(operands[1])
        if abs(imm) >= 2**20:
            return None  # Illegal immediate value
        return assemble_u_type(instruction, rd, imm)

    elif instruction == "jal":
        if len(operands) != 2:
            return None  # Incorrect number of operands
        rd = int(operands[0])
        label = operands[1]
        imm = symbol_table[label] - len(symbol_table)
        if abs(imm) >= 2**20:
            return None  # Illegal immediate value
        return assemble_j_type(instruction, rd, imm)

    else:
        return None  # Invalid instruction








#Assemble the entire program
def assemble_program(input_file, output_file):
    symbol_table = {}
    binary_code = []

    #Building symbol table
    with open(input_file, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            tokens = re.split(r'[,\s]+', line)
            if tokens[0].endswith(':'):
                label = tokens[0][:-1]
                if label in symbol_table:
                    print(f"Error: Duplicate label '{label}' found on line {line_number}")
                    return
                symbol_table[label] = len(binary_code)
                tokens = tokens[1:]

    #Assembling instructions
    with open(input_file, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            instruction, operands = parse_instruction(line)
            binary_instruction = assemble_instruction(instruction, operands, symbol_table)
            if binary_instruction is None:
                print(f"Error: Invalid instruction '{instruction}' found on line {line_number}")
                return
            binary_code.append(binary_instruction)

    #Check if Virtual Halt is last instruction
    if binary_code[-1] != opcode_dict["halt"]:
        print("Error: Virtual Halt instruction must be used as the last instruction")
        return

    #Write binary output to output file
    with open(output_file, 'w') as file:
        for instruction in binary_code:
            file.write(instruction + '\n')





#MDriver code
if __name__ == "__main__":
    input_file = "input.asm"
    output_file = "output.txt"
    assemble_program(input_file, output_file)
