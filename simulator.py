from dictionaries import *
import sys

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
    
def convert_to_hex(binary_str):    #convert 32-bit binary to 8-bit hex
    binary_str = binary_str.zfill(((len(binary_str) + 3) // 4) * 4)

    hex_str = hex(int(binary_str, 2))[2:].upper()

    if len(hex_str) > 8:
        hex_str = hex_str[-8:]

    return hex_str.zfill(8)


def unsigned(value):    #Perform unsigned integer conversion.

    return value & 0xFFFFFFFF


# def mem_dump(mem_store, start_address, end_address, f, step = 4):
#     for address in range(start_address, end_address + 1, step):
#         # Check if the address is in the dictionary
#         if address in mem_store:
#             data = mem_store[address]
#         else:
#             data = 0  # default value for uninitialized memory addresses

#         # Format the data as 32-bit binary
#         data_binary = format(data, '032b')
#         # Print the address and the data
#         f.write(f"0x{address:08X}:0b{data_binary}")
#         f.write('\n')


def PC_dump(PC, f):    #Dump the program counter (PC) value.

    PC_register = (list(binary(PC)))
    string = "".join(PC_register)
    f.write("0b" + string + " ")


def reg_dump(reg_value, f):    #Dump the register values.

    for register in reg_value:
        if (register!='zero'):
            f.write("0b" + binary(reg_value[register]) + " ")

    f.write('\n')


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

    if Instruction == '00000000000000000000000001100011':
        halt = True

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
                #mem_store[rd] = rs1 - rs2
        else:
            # Addition
            if funct3 == '000':
                reg_value[rd] = rs2 + rs1
                #mem_store[rd] = rs1 + rs2
                #print(reg_value[rd]) debug statement;
            # Shift left logical
            elif funct3 == '001':
                shift_val = rs2 & 0b11111
                reg_value[rd] = rs1 << shift_val
                #mem_store[rd] = rs1 << shift_val

            # Shift right logical
            elif funct3 == '101':
                shift_val = rs2 & 0b11111
                reg_value[rd] = rs1 >> shift_val
                #mem_store[rd] = rs1 >> shift_val
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

     # S-type instruction handling
    elif opcode == '0100011':  # sw
        imm_11_5 = Instruction[0:7]
        rs2_addr = Instruction[7:12]
        rs1_addr = Instruction[12:17]
        imm_4_0 = Instruction[20:25]
        imm = int((imm_11_5 + imm_4_0),2)
        rs2 = reg_value[registers_Dictionary[rs2_addr]]
        rs1 = reg_value[registers_Dictionary[rs1_addr]]
        int1=(rs1+imm)
        bin1=binary(int1)
        hex1=convert_to_hex(str(bin1))
        hex_str="0x"+str(hex1)

        for key in mem_store:
            if key==hex_str:
                mem_store[key]=binary(rs2)
                break

    # U-type instruction handling
    elif opcode == '0110111':  # lui
        rd_addr = Instruction[20:25]
        imm = Instruction[0:20]
        rd = registers_Dictionary[rd_addr]
        reg_value[rd] = sign_extend(int(imm, 2), 20)
        #mem_store[rd] = reg_value[rd]

    elif opcode == '0010111':  # auipc
        rd_addr = Instruction[20:25]
        imm = Instruction[0:20]
        rd = registers_Dictionary[rd_addr]
        reg_value[rd] = PC + sign_extend(int(imm, 2), 20)
        #mem_store[rd] = reg_value[rd]
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
        #mem_store[address] = reg_value[rd]
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
        #mem_store[rd] = reg_value[rd]
        PC = (rs1 + sign_extend(int(imm, 2), 12)) & 0xFFFFFFFE  # Make LSB 0

    return PC, mem_store, reg_value, halt



# Check if the correct number of command line arguments are provided
if len(sys.argv) != 3:
    print("Usage: python file.py input_file.txt output_file.txt")
    sys.exit(1)

# Read input from the input file
input_file = sys.argv[1]
output_file = sys.argv[2]
with open(input_file, 'r') as f:
    input_data = f.read().rstrip()

instructions = input_data.split("\n")

#mem_store = {i: 0 for i in range(32)}
PC = 4
halt = False

with open(output_file, 'w') as f:

    while not halt:
        if len(instructions) == 0:
            break

        for i, Instruction in enumerate(instructions):
            PC_dump(PC, f)
            PC, mem_store, reg_value, halt = ee_execute(Instruction, PC, mem_store, reg_value)
            PC = pc_update(PC)
            reg_dump(reg_value, f)
            print()

            if halt:
                break

        if PC >= len(instructions):
            break

with open(output_file, 'a') as f:
    for key in mem_store:
        f.write(key + ":" + mem_store[key] + '\n')

# mem_dump(mem_store, 0x0010000, 0x0001007C)
