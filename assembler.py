import re
# Define dictionaries for opcode and funct3 encoding
opcode_dict = {
    "add": "0110011", "sub": "0110011", "sll": "0110011",
    "slt": "0110011", "sltu": "0110011", "xor": "0110011",
    "srl": "0110011", "or": "0110011", "and": "0110011",
    "lw": "0000011", "addi": "0010011", "sltiu": "0010011",
    "jalr": "1100111", "sw": "0100011", "beq": "1100011",
    "bne": "1100011", "blt": "1100011", "bge": "1100011",
    "bltu": "1100011", "bgeu": "1100011", "lui": "0110111",
    "auipc": "0010111", "jal": "1101111", "mul": "0110011",
    "rst": "0110111", "halt": "0110111", "rvrs": "0110111",
    "div": "0110011", "rem": "0110011",  # New instructions
}

funct3_dict = {
    "add": "000", "sub": "000", "sll": "001",
    "slt": "010", "sltu": "011", "xor": "100",
    "srl": "101", "or": "110", "and": "111",
    "lw": "010", "addi": "000", "sltiu": "011",
    "jalr": "000", "sw": "010", "beq": "000",
    "bne": "001", "blt": "100", "bge": "101",
    "bltu": "110", "bgeu": "111", "mul": "000",
    "rst": "000", "halt": "001", "rvrs": "010",
    "div": "100", "rem": "110",  # New funct3 values
}

# Define a function to convert a decimal number to a binary string with specified width
def dec_to_bin(dec_num, width):
    return format(dec_num, '0' + str(width) + 'b')

# Define a function to assemble R-type instructions
def assemble_r_type(instruction, rd, rs1, rs2):
    opcode = opcode_dict[instruction]
    funct3 = funct3_dict[instruction]
    funct7 = "0000000"  # Default value for R-type
    return funct7 + dec_to_bin(rs2, 5) + dec_to_bin(rs1, 5) + funct3 + dec_to_bin(rd, 5) + opcode

# Define a function to assemble I-type instructions
def assemble_i_type(instruction, rd, rs1, imm):
    opcode = opcode_dict[instruction]
    funct3 = funct3_dict[instruction]
    return dec_to_bin(imm, 12) + dec_to_bin(rs1, 5) + funct3 + dec_to_bin(rd, 5) + opcode

# Define a function to assemble S-type instructions
def assemble_s_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = funct3_dict[instruction]
    imm_11_5 = dec_to_bin(imm >> 5, 7)
    imm_4_0 = dec_to_bin(imm & 0x1F, 5)
    return imm_11_5 + dec_to_bin(rs2, 5) + dec_to_bin(rs1, 5) + funct3 + imm_4_0 + opcode

# Define a function to assemble B-type instructions
def assemble_b_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = funct3_dict[instruction]
    imm_12 = dec_to_bin((imm >> 12) & 1, 1)
    imm_10_5 = dec_to_bin((imm >> 5) & 0x3F, 6)
    imm_4_1 = dec_to_bin((imm >> 1) & 0xF, 4)
    imm_11 = dec_to_bin((imm >> 11) & 1, 1)
    return imm_12 + imm_10_5 + dec_to_bin(rs2, 5) + dec_to_bin(rs1, 5) + funct3 + imm_4_1 + imm_11 + opcode

# Define a function to assemble U-type instructions
def assemble_u_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    return dec_to_bin(imm, 20) + dec_to_bin(rd, 5) + opcode

# Define a function to assemble J-type instructions
def assemble_j_type(instruction, rd, imm):
    opcode = opcode_dict[instruction]
    imm_20 = dec_to_bin((imm >> 20) & 1, 1)
    imm_10_1 = dec_to_bin((imm >> 1) & 0x3FF, 10)
    imm_11 = dec_to_bin((imm >> 11) & 1, 1)
    imm_19_12 = dec_to_bin((imm >> 12) & 0xFF, 8)
    return imm_20 + imm_10_1 + imm_11 + imm_19_12 + dec_to_bin(rd, 5) + opcode

# Define a function to parse assembly instructions
def parse_instruction(line):
    line = line.strip()
    tokens = re.split(r'[,\s]+', line)
    instruction = tokens[0]
    operands = tokens[1:]
    return instruction, operands

# Define a function to assemble instructions
def assemble_instruction(instruction, operands, symbol_table):
    opcode = opcode_dict.get(instruction)
    if not opcode:
        return None  # Invalid instruction

    if instruction in ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and",
                       "mul", "rst", "halt", "rvrs", "div", "rem"]:  # Include "div" and "rem"
        rd, rs1, rs2 = map(int, operands)
        return assemble_r_type(instruction, rd, rs1, rs2)

    elif instruction in ["lw", "addi", "sltiu", "jalr"]:
        rd, rs1 = map(int, operands[:2])
        imm = int(operands[2])
        return assemble_i_type(instruction, rd, rs1, imm)

    elif instruction == "sw":
        rs1, rs2 = map(int, operands[:2])
        imm = int(operands[2])
        return assemble_s_type(instruction, rs1, rs2, imm)

    elif instruction in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
        rs1, rs2 = map(int, operands[:2])
        label = operands[2]
        imm = symbol_table[label] - len(symbol_table)
        return assemble_b_type(instruction, rs1, rs2, imm)

    elif instruction in ["lui", "auipc"]:
        rd = int(operands[0])
        imm = int(operands[1])
        return assemble_u_type(instruction, rd, imm)

    elif instruction == "jal":
        rd = int(operands[0])
        label = operands[1]
        imm = symbol_table[label] - len(symbol_table)
        return assemble_j_type(instruction, rd, imm)

    else:
        return None  # Invalid instruction

# Define a function to assemble the entire program
def assemble_program(input_file, output_file):
    symbol_table = {}
    binary_code = []

    # First pass to build symbol table
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

    # Second pass to assemble instructions
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

    # Write binary instructions to output file
    with open(output_file, 'w') as file:
        for instruction in binary_code:
            file.write(instruction + '\n')

# Main function to run the assembler
if __name__ == "__main__":
    input_file = "input.asm"
    output_file = "output.txt"
    assemble_program(input_file, output_file)
