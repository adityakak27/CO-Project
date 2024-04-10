import re
import sys
from dictionaries import *


# Global variables
PC = 0
memory = [0] * 32  # Memory initialization

# Helper functions
def binary(number, size=12):
    if number < 0:
        number = 2 ** size + number
    binary_string = bin(number)[2:]
    padded_binary_string = binary_string.zfill(size)
    return padded_binary_string

def assemble_program(input_file, output_file):
    binary_code = []
    vHalt_found = False

    with open(input_file, 'r') as file:
        for line_number, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            instruction, operands = parse_instruction(line)
            binary_instruction = assemble_instruction(instruction, operands)
            if binary_instruction is None:
                print(f"Error: Invalid instruction '{instruction}' found on line {line_number}.")
                return
            binary_code.append(binary_instruction)

            if instruction == "beq" and set(operands) == {"0", "zero"}:
                vHalt_found = True
                break

    if not vHalt_found:
        print("Error: Virtual Halt Command Not Found.")
        return

    with open(output_file, 'w') as file:
        for instruction in binary_code:
            file.write(instruction + '\n')



def parse_instruction(line):
    line = line.strip()
    tokens = [token for token in re.split(r'[,\s\(\)]+', line) if token] #splitting the input line into 'tokens';
    instruction = tokens[0] #above tokens are categorised into instruction and operands
    operands = tokens[1:]
    return instruction, operands


def assemble_instruction(instruction, operands):
    #check if all operands are valid or immediate values are numbers (adjusted for negative values)
    for operand in operands:
        if operand not in registers_Dictionary and (operand.isdigit() or (operand.startswith('-') and operand[1:].isdigit())):
            return None # any one operand or imm is found to be invalid

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
            return None 
        rs1, rs2, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  
            imm = int(imm)
            if abs(imm) >= 2**12:
                return None 
        else:
            return None  
        return assemble_s_type(instruction, rs1, rs2, imm)

    elif instruction in ["beq", "bne", "blt", "bge", "bltu", "bgeu"]:
        if len(operands) != 3:
            return None  
        rs1, rs2, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  
            imm = int(imm)
            if abs(imm) >= 2**12:
                return None 
        else:
            return None

    elif instruction in ["lui", "auipc"]:
        if len(operands) != 2:
            return None  
        rd, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  
            imm = int(imm)
            if abs(imm) >= 2**20:
                return None 
        else:
            return None 
        return assemble_u_type(instruction, rd, imm)

    elif instruction == "jal":
        if len(operands) != 2:
            return None  
        rd, imm = operands
        if imm.isdigit() or (imm.startswith('-') and imm[1:].isdigit()):  
            imm = int(imm)
            if abs(imm) >= 2**20:
                return None
        else:
            return None 
        return assemble_j_type(instruction, rd, imm)

    else:
        return None   #instruction provided is invalid

def assemble_r_type(instruction, rd, rs1, rs2):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    if instruction == 'sub':
        funct7 = "0100000" #default
    else:
        funct7 = "0000000" #default
    return funct7 + registers_Dictionary[rs2] + registers_Dictionary[rs1] + funct3 + registers_Dictionary[rd] + opcode

def assemble_i_type(instruction, rd, rs1, imm):
    opcode = opcode_dict[instruction] 
    funct3 = functions_dict[instruction] #getting opcode and function in binary from the respective dictionaries 
    imm_binary = binary(imm) #changing int immediate to binary
    imm_binary = imm_binary[-12:]  #reversing immediate
    return imm_binary + registers_Dictionary[rs1] + funct3 + registers_Dictionary[rd] + opcode #final binary output for entire line

def assemble_s_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_binary = binary(imm)
    imm_binary = imm_binary[-12:]  
    imm_11_5 = imm_binary[:7]
    imm_4_0 = imm_binary[7:]
    return imm_11_5 + registers_Dictionary[rs2] + registers_Dictionary[rs1] + funct3 + imm_4_0 + opcode

def assemble_b_type(instruction, rs1, rs2, imm):
    opcode = opcode_dict[instruction]
    funct3 = functions_dict[instruction]
    imm_binary = binary(imm, 13)
    imm_binary = imm_binary[-13:]  
    imm_12 = imm_binary[0]
    imm_10_5 = imm_binary[1:7]  #splitting the immediate
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


def PC_update(PC):
    global instructions
    next_PC = PC + 1
    if "jal" in instructions[PC]:
        jump_address = int(instructions[PC].split()[-1][1:])
        next_PC = jump_address
    return next_PC

def main():
    global PC, instructions
   # if len(sys.argv) != 3:
    #    print("Usage: python file.py <input_file> <output_file>")
     #   return
    
    #input_file = sys.argv[1]
    #output_file = sys.argv[2]
    
    input_file = "input.txt"
    output_file = "output.txt"

    with open(input_file, 'r') as f:
        instructions = f.readlines()
    
    while PC < len(instructions):
        instruction = instructions[PC].strip()
        if not instruction or instruction.startswith('#'):
            PC += 4
            continue
        
        opcode = instruction.split()[0]
        if opcode == "jal":
            memory[PC] = PC + 4  # Store the link address
        parsed_instruction = parse_instruction(instruction)
        if parsed_instruction is None:
            print(f"Error: Unable to parse instruction '{instruction}' at PC = {PC}.")
            return
        binary_instruction = assemble_instruction(*parsed_instruction)
        if binary_instruction is None:
            print(f"Error: Invalid instruction '{instruction}' found at PC = {PC}.")
            return
        memory[PC] = binary_instruction
        PC = PC_update(PC)
    
    with open(output_file, 'w') as f:
        for instruction in memory:
            f.write(f"{instruction}\n")
        

main()
