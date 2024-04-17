from dictionaries import *
import sys

def get_input():    #Get input instructions from the user.

    print("Enter instructions (one per line, or 'exit' to quit):")
    instructions = []
    while True:
        line = input()
        if line.lower() == 'exit':
            break
        instructions.append(line)
    return instructions

def binary(number, size=32):    #Convert a number to binary representation with a specified size.

    if number < 0:
        number = 2 ** size + number
    binary_string = bin(number)[2:]
    padded_binary_string = binary_string.zfill(size)
    return padded_binary_string

def convert_to_bin(number):     #Convert a number to 16-bit binary representation.
    if number < 0:
        return binary(number, 16)
    else:
        b = list(bin(number)[2:])
        unused = []
        if len(b) < 16:
            for i in range(16-len(b)):
                unused.append("0")
        binary_string = "".join(unused + b)
        return binary_string


def unsigned(value):    #Perform unsigned integer conversion.

    return value & 0xFFFFFFFF


def mem_dump(mem_store, start_address, end_address, step = 4):
    for address in range(start_address, end_address + 1, step):
        # Check if the address is in the dictionary
        if address in mem_store:
            data = mem_store[address]
        else:
            data = 0  # default value for uninitialized memory addresses

        # Format the data as 32-bit binary
        data_binary = format(data, '032b')
        # Print the address and the data
        print(f"0x{address:08X}:0b{data_binary}")


def PC_dump(PC):    #Dump the program counter (PC) value.

    PC_register = (list(binary(PC)))
    string = "".join(PC_register)
    print(string, end=" ")


def reg_dump(reg_value):    #Dump the register values.

    for register in reg_value:
        if (register!='zero'):
            print(binary(reg_value[register]), end=" ")


def pc_update(PC):    #Update the program counter (PC) value.

    PC += 4
    return PC


def sign_extend(imm, length):   #Sign extend the immediate value

    if (imm >> (length - 1)) & 1:
        return imm | ((-1 << length) & 0xFFFFFFFF)
    return imm


def ee_execute(Instruction, PC, mem_store, reg_value):  #Execute the given instruction.

    cycle = 0
    halt = False
    x = []
    y = []
    check = 0

    cycle += 1
    y.append(PC)
    x.append(cycle)
    check = 0
    opcode = Instruction[25:]

    # R-type instruction handling
    if opcode == '0110011':
        funct3 = Instruction[17:20]
        funct7 = Instruction[0:7]

        rs1_addr = Instruction[12:17]
        rs2_addr = Instruction[7:12]
        rd_addr = Instruction[20:25]

        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        rs2 = reg_value[registers_Dictionary[rs2_addr]]
        rd = registers_Dictionary[rd_addr]

        if funct7 == '0100000':
            # Subtraction
            if rs2 > rs1:
                reg_twos = binary(-rs2, 32)
                reg_value[rd] = unsigned(reg_twos) + rs1
            else:
                reg_value[rd] = rs1 - rs2
                mem_store[rd] = rs1 - rs2
        else:
            # Addition
            if funct3 == '000':
                reg_value[rd] = rs2 + rs1
                mem_store[rd] = rs1 + rs2
                #print(reg_value[rd]) debug statement;
            # Shift left logical
            elif funct3 == '001':
                shift_val = rs2 & 0b11111
                reg_value[rd] = rs1 << shift_val
                mem_store[rd] = rs1 << shift_val

            # Shift right logical
            elif funct3 == '101':
                shift_val = rs2 & 0b11111
                reg_value[rd] = rs1 >> shift_val
                mem_store[rd] = rs1 >> shift_val
            # Bitwise XOR
            elif funct3 == '100':
                reg_value[rd] = rs1 ^ rs2
            # Bitwise OR
            elif funct3 == '110':
                reg_value[rd] = rs1 | rs2
            # Bitwise AND
            elif funct3 == '111':
                reg_value[rd] = rs1 & rs2
    # B-type instruction handling
    elif opcode == '1100011':
        imm_value = Instruction[0] + Instruction[7:11] + Instruction[1:7] + '0'
        rs2_addr = Instruction[20:25]
        rs1_addr = Instruction[15:20]
        funct3 = Instruction[12:15]

        rs2 = reg_value[registers_Dictionary[rs2_addr]]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        imm_value = sign_extend(int(imm_value, 2), 13)

        # Branch on equal (beq)
        if funct3 == '000':
            if rs1 == rs2:
                PC += imm_value
        # Branch on not equal (bne)
        elif funct3 == '001':
            if rs1 != rs2:
                PC += imm_value
        # Branch on less than (blt)
        elif funct3 == '100':
            if rs1 < rs2:
                PC += imm_value
        # Branch on greater than or equal to (bge)
        elif funct3 == '101':
            if rs1 >= rs2:
                PC += imm_value
        # Branch on less than, unsigned (bltu)
        elif funct3 == '110':
            if unsigned(rs1) < unsigned(rs2):
                PC += imm_value
        # Branch on greater than or equal to, unsigned (bgeu)
        elif funct3 == '111':
            if unsigned(rs1) >= unsigned(rs2):
                PC += imm_value

    # # S-type instruction handling
    # elif opcode == '0100011':  # sw
    #     imm_11_5 = int(Instruction[25:32])
    #     rs2_addr = Instruction[20:25]
    #     rs1_addr = Instruction[15:20]
    #     imm_4_0 = int(Instruction[7:12])
    #     imm = sign_extend((imm_11_5 + (imm_4_0 << 5), 2), 12)
    #     rs2 = reg_value[registers_Dictionary[rs2_addr]]
    #     rs1 = reg_value[registers_Dictionary[rs1_addr]]
    #     mem_store[rs1 + imm] = rs2

     # S-type instruction handling
    elif opcode == '0100011':  # sw
        imm_11_5 = int(Instruction[25:32], 2)
        rs2_addr = Instruction[20:25]
        rs1_addr = Instruction[15:20]
        imm_4_0 = int(Instruction[7:12], 2)
        imm = sign_extend(imm_11_5 + (imm_4_0 << 5), 12)
        rs2 = reg_value[registers_Dictionary[rs2_addr]]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]

    # U-type instruction handling
    elif opcode == '0110111':  # lui
        rd_addr = Instruction[20:25]
        imm = Instruction[0:20]
        rd = registers_Dictionary[rd_addr]
        reg_value[rd] = sign_extend(int(imm, 2), 20)
        mem_store[rd] = reg_value[rd]

    elif opcode == '0010111':  # auipc
        rd_addr = Instruction[20:25]
        imm = Instruction[0:20]
        rd = registers_Dictionary[rd_addr]
        reg_value[rd] = PC + sign_extend(int(imm, 2), 20)
        mem_store[rd] = reg_value[rd]
    # J-type instruction handling
    elif opcode == '1101111':
        rd_addr = Instruction[20:25]
        imm = (
            (int(Instruction[0]) << 20)
            | (int(Instruction[1:11], 2) << 1)
            | (int(Instruction[11]) << 11)
            | (int(Instruction[12:20], 2) << 12)
        )
        imm = sign_extend(imm, 21)
        rd = registers_Dictionary[rd_addr]
        reg_value[rd] = PC + 4
        PC += imm

    # I-type instruction handling
    elif opcode == '0000011':  # lw
        rd_addr = Instruction[20:25]
        rs1_addr = Instruction[12:17]
        imm = Instruction[0:12]
        rd = registers_Dictionary[rd_addr]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        address = rs1 + sign_extend(int(imm, 2), 12)
        reg_value[rd] = mem_store.get(address, 0)  # Using 0 as a default value
        mem_store[address] = reg_value[rd]
    elif opcode == '0010011':
        rd_addr = Instruction[20:25]
        rs1_addr = Instruction[12:17]
        imm = Instruction[0:12]
        funct3 = Instruction[17:20]
        rd = registers_Dictionary[rd_addr]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        if funct3 == '000':  # addi
            reg_value[rd] = rs1 + sign_extend(int(imm, 2), 12)
        elif funct3 == '011':  # sltiu
            reg_value[rd] = 1 if unsigned(rs1) < unsigned(sign_extend(int(imm, 2), 12)) else 0
    elif opcode == '1100111':  # jalr
        rd_addr = Instruction[20:25]
        rs1_addr = Instruction[12:17]
        imm = Instruction[0:12]
        rd = registers_Dictionary[rd_addr]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        reg_value[rd] = PC + 4
        mem_store[rd] = reg_value[rd]
        PC = (rs1 + sign_extend(int(imm, 2), 12)) & 0xFFFFFFFE  # Make LSB 0

    return PC, mem_store, reg_value, halt


#instructions = get_input()

instructions = ["00000000000000000000010010110011",
"00000000000000000000100100110011",
"00000000000100000000010010010011",
"00000001000000000000100100010011",
"00000001001001001001010010110011",
"00000000101100000000101010010011",
"00000001010101001010000000100011",
"00000000000001001010100100000011",
"00000000010001001000010010010011",
"00000000000100000000100110010011",
"00000001001110010111100100110011",
"00000001001000000000100001100011",
"00000000001100000000101000010011",
"00000001010001001010000000100011",
"00000000000000000000000001100011",
"00000000001000000000101000010011",
"00000001010001001010000000100011",
"00000000000000000000000001100011"]

# Check if the correct number of command line arguments are provided
#if len(sys.argv) != 3:
 #   print("Usage: python file.py input_file.txt output_file.txt")
  #  sys.exit(1)

# Read input from the input file
#input_file = sys.argv[1]
#with open(input_file, 'r') as f:
#    input_data = f.read().rstrip()

#instructions = input_data.split("\n")

mem_store = {i: 0 for i in range(32)}
PC = 4
halt = False


while not halt:
    if len(instructions) == 0:
        break

    for i, Instruction in enumerate(instructions):
        PC_dump(PC)
        PC, mem_store, reg_value, halt = ee_execute(Instruction, PC, mem_store, reg_value)
        PC = pc_update(PC)
        reg_dump(reg_value)
        print()

        if halt:
            break

    if PC >= len(instructions):
        break

mem_dump(mem_store, 0x0010000, 0x0001007C)
