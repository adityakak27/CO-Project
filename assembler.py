import re
from dictionaries import * #importing dictionaries from dictionaries.py to avoid cluttering of code

def binary(number, size = 12):
    if number < 0:
        number = 2 ** size + number
    binary_string = bin(number)[2:]
    padded_binary_string = binary_string.zfill(size)
    return padded_binary_string



def assemble_r_type(instruction, rd, rs1, rs2):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    funct7 = "0000000"  # default
    return funct7 + registers_Dictionary[rs2] + registers_Dictionary[rs1] + funct3 + registers_Dictionary[rd] + opcode

def assemble_i_type(instruction, rd, rs1, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_binary = binary(imm)
    imm_binary = imm_binary[-12:]  #take the last 12 bits
    return imm_binary + registers_Dictionary[rs1] + funct3 + registers_Dictionary[rd] + opcode

def assemble_s_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_binary = binary(imm)
    imm_binary = imm_binary[-12:]  #take the last 12 bits
    imm_11_5 = imm_binary[:7]
    imm_4_0 = imm_binary[7:]
    return imm_11_5 + registers_Dictionary[rs2] + registers_Dictionary[rs1] + funct3 + imm_4_0 + opcode

def assemble_b_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_binary = binary(imm, 13)
    imm_binary = imm_binary[-13:]  #take the last 13 bits
    imm_12 = imm_binary[0]
    imm_10_5 = imm_binary[1:7]
    imm_4_1 = imm_binary[7:11]
    imm_11 = imm_binary[11]
    return imm_12 + imm_10_5 + registers_Dictionary[rs2] + registers_Dictionary[rs1] + funct3 + imm_4_1 + imm_11 + opcode

def assemble_u_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    imm_binary = binary(imm, 20)
    imm_binary = imm_binary[-20:]  
    return imm_binary + registers_Dictionary[rd] + opcode

def assemble_j_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    imm_binary = binary(imm, 21)
    imm_binary = imm_binary[-21:] 
    imm_20 = imm_binary[0]
    imm_10_1 = imm_binary[1:11]
    imm_11 = imm_binary[11]
    imm_19_12 = imm_binary[12:20]
    return imm_20 + imm_10_1 + imm_11 + imm_19_12 + registers_Dictionary[rd] + opcode

def parse_instruction(line):
    line = line.strip()
    tokens = [token for token in re.split(r'[,\s\(\)]+', line) if token]
    instruction = tokens[0]
    operands = tokens[1:]
    return instruction, operands



def assemble_instruction(instruction, operands):
    operands = sorted(operands, key=lambda x: (x.startswith('-'), x.isdigit(), x))
    if instruction not in instructions_Dictionary:
        return None  # invalid instruction

    # Check if all operands are valid registers or immediate values
    for operand in operands:
        if operand not in registers_Dictionary and not (operand.isdigit() or (operand.startswith('-') and operand[1:].isdigit())):
            return None
  # invalid operand

    if instruction in ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and",
                       "mul", "rst", "halt", "rvrs", "div", "rem"]:
        if len(operands) != 3:
            return None  # incorrect no of operands
        rd, rs1, rs2 = operands
        return assemble_r_type(instruction, rd, rs1, rs2)

    elif instruction in ["lw", "addi", "sltiu", "jalr"]:
        if len(operands) != 3:
            return None  # incorrect no of operands
        rd, rs1, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  # Check if immediate value
            imm = int(imm)
            if abs(imm) >= 2**12:
                return None  # illegal imm value
        else:
            return None  # immediate value must be an integer
        return assemble_i_type(instruction, rd, rs1, imm)

    elif instruction == "sw":
        if len(operands) != 3:
            return None  # incorrect no of operands
        rs1, rs2, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  # Check if immediate value
            imm = int(imm)
            if abs(imm) >= 2**12:
                return None  # illegal imm value
        else:
            return None  # immediate value must be an integer
        return assemble_s_type(instruction, rs1, rs2, imm)

    elif instruction in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
        if len(operands) != 3:
            return None  # incorrect no of operands
        rs1, rs2, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  # Check if immediate value
            imm = int(imm)
            if abs(imm) >= 2**12:
                return None  # illegal imm value
        else:
            return None  # immediate value must be an integer
        return assemble_b_type(instruction, rs1, rs2, imm)

    elif instruction in ["lui", "auipc"]:
        if len(operands) != 2:
            return None  # incorrect no of operands
        rd, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  # Check if immediate value
            imm = int(imm)
            if abs(imm) >= 2**20:
                return None  # illegal imm value
        else:
            return None  # immediate value must be an integer
        return assemble_u_type(instruction, rd, imm)

    elif instruction == "jal":
        if len(operands) != 2:
            return None  # incorrect no of operands
        rd, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  # Check if immediate value
            imm = int(imm)
            if abs(imm) >= 2**20:
                return None  # illegal imm value--
        else:
            return None  # immediate value must be an integer
        return assemble_j_type(instruction, rd, imm)

    else:
        return None  # invalid instruction




def assemble_program(input_file, output_file):
    binary_code = []

    with open(input_file, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            instruction, operands = parse_instruction(line)
            binary_instruction = assemble_instruction(instruction, operands)
            if binary_instruction is None:
                print(f"Error: Invalid instruction '{instruction}' found on line {line_number}")
                return
            binary_code.append(binary_instruction)

 #   if binary_code[-1] != opcode_dict["halt"]:
  #      print("Error: Virtual Halt must be used as the last instruction")
 #       return

    with open(output_file, 'w') as file:
        for instruction in binary_code:
            file.write(instruction + '\n')


# driver code
if __name__ == "__main__":
    input_file = "input.txt"
    output_file = "output.txt"
    assemble_program(input_file, output_file)
