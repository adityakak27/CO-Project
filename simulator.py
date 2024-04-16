from dictionaries import *
import sys



input='''00000000000000000000010010110011
         00000000000000000000100100110011
         00000000000100000000010010010011
         00000001000000000000100100010011
         00000001001001001001010010110011
         00000000101100000000101010010011
         00000001010101001010000000100011
         00000000000001001010100100000011
         00000000010001001000010010010011
         00000000000100000000100110010011
         00000001001110010111100100110011
         00000001001000000000100001100011
         00000000001100000000101000010011
         00000001010001001010000000100011
         00000000000000000000000001100011
         00000000001000000000101000010011
         00000001010001001010000000100011
         00000000000000000000000001100011'''
input = input.rstrip()
instructions = input.split("\n")
x = []
y = []


# Check if the correct number of command line arguments are provided
#if len(sys.argv) != 3:
 #   print("Usage: python file.py input_file.txt output_file.txt")
  #  sys.exit(1)

# Read input from the input file
#input_file = sys.argv[1]
#with open(input_file, 'r') as f:
#    input_data = f.read().rstrip()

#instructions = input_data.split("\n")


#stores line no. and register value whenever variables are used
mem_store = {}

reg = registers_Dictionary


def binary(number, size = 12): #default size set to 12; specified otherwise if necessary 
    if number < 0:
        number = 2 ** size + number
    binary_string = bin(number)[2:]
    padded_binary_string = binary_string.zfill(size)
    return padded_binary_string


#def twos_binary_subtract(r1, r2):
    #placeholder


#converts decimal to 16-bit binary number
def convert_to_bin(number):
    if '.' in str(number):
        s = str(number).split(".")
        int1 = s[0]
        dec1 = float('0'+'.'+s[1])
        int1 = bin(int(int1))[2:]
        int2 = ''
        int2 += int1
        int2 +='.'
        for i in range(5):
            dec1 = dec1*2
            s = str(dec1).split(".")
            int1 = s[0]
            int2 += int1
            dec1 = float('0'+'.'+s[1])
        exp = len(int2.split('.')[0])-1
        if exp > 7:
            exp = 0
            return 99
        else:
            float1 = bin(exp)[2:]
        s = int2.split('.')[0] + int2.split('.')[1]
        for i in s[6:]:
            if i =='1':
                return 88
        s = s[1:6]
        float1 = float1 + s
        l = ''
        for i in range(16 - len(float1)):
            l += '0'
        l = l + float1
        return l
    else:
        b = list(bin(number))[2:]
        unused = []
        if len(b) < 16:
            for i in range(0,16-len(b)):
                unused.append("0")
        binary = "".join(((unused)+(b))[-16:])
        return binary

def unsigned(value):
    return value & 0xFFFFFFFF

#converts binary to float
def convertback(n):
    dec = 0
    for i in range(3):
        dec += int(n[i])*(2**(2-i))
    s2 ='1'+ n[3:]
    s3 = s2[:dec+1] + '.' + s2[dec+1:]
    s3 = s3.split('.')
    final = finaldec = 0
    for i in range(len(s3[0])):
        final += int(s3[0][i]) * (2**(len(s3[0])-1-i))
    for i in range(len(s3[1])):
        finaldec += int(s3[1][i]) * (2**( -1* (i + 1)))
    final = str(final + finaldec)
    return float(final)

def mem_dump():
    global instructions
    global mem_store
    i = 0
    for line in instructions:
        print(line)
        i += 1

    mem = sorted(mem_store.keys())
    for item in mem:
        if(len(mem) == 0):
            break
        while(item != i):
            print("0000000000000000")
            i += 1
        print(convert_to_bin(mem_store[item]))
        i += 1

    while(i < 256):
        print("0000000000000000")
        i += 1

def PC_dump():
    global PC
    PC_register = (list(convert_to_bin(PC)))[8:] #changes PC value form deicmal to 16 bit to 8 bit binary
    string = "".join(PC_register)
    print(string,end = " ")

def reg_dump():
    for register in reg_value:
        print(convert_to_bin(reg_value[register]),end = " ")
    print("000000000000",end = "")



def pc_update(PC):
    return PC

def sign_extend(imm, length):
        # Sign extend the immediate value
        if (imm >> (length - 1)) & 1:
            return imm | ((-1 << length) & 0xFFFFFFFF)
        return imm

def ee_execute(Instruction):
    global cycle , PC , check , halt
    
    cycle += 1
    y.append(PC)
    x.append(cycle)
    check = 0
    opcode = Instruction[-1:-7]
    #r - type
    if(opcode == '0110011'):
        funct3 = Instruction[-14:-12]
        funct7 = Instruction[0:7]

        rs1 = reg[(Instruction)[7:10]]
        rs2 = reg[(Instruction)[10:13]]
        rd = reg[(Instruction)[13:16]]


        if funct7 == '0100000':
        # Subtraction
            if reg_value[rs2] > reg_value[rs1]:
                reg_twos = binary(-reg_value[rs2], 32)
                reg_value[rd] = reg_twos + reg_value[rs1]
            else:
                reg_value[rd] = reg_value[rs1] - reg_value[rs2]
        else: 
            # Addition
            if funct3 == '000':
                reg_value[rd] = reg_value[rs2] + reg_value[rs1]
            # Shift left logical
            elif funct3 == '001':
                shift_val = reg_value[rs2] & 0b11111
                reg_value[rd] = reg_value[rs1] << shift_val
            # Shift right logical
            elif funct3 == '101':
                shift_val = reg_value[rs2] & 0b11111
                reg_value[rd] = reg_value[rs1] >> shift_val
            # Bitwise XOR
            elif funct3 == '100':
                reg_value[rd] = reg_value[rs1] ^ reg_value[rs2]
            # Bitwise OR
            elif funct3 == '110':
                reg_value[rd] = reg_value[rs1] | reg_value[rs2]
            # Bitwise AND
            elif funct3 == '111':
                reg_value[rd] = reg_value[rs1] & reg_value[rs2]
                
        PC += 1

    #b - type
    elif(opcode == '1100011'):
        imm_value = Instruction[0] + Instruction[7:11] + Instruction[1:7] + '0'
        rs2 = Instruction[20:25]
        rs1 = Instruction[15:20]
        funct3 = Instruction[12:15]
        # Branch on equal (beq)
        if funct3 == '000':
            if reg_value[rs1] == reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        # Branch on not equal (bne)
        elif funct3 == '001':
            if reg_value[rs1] != reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        # Branch on less than (blt)
        elif funct3 == '100':
            if reg_value[rs1] < reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        # Branch on greater than or equal to (bge)
        elif funct3 == '101':
            if reg_value[rs1] >= reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        # Branch on less than, unsigned (bltu)
        elif funct3 == '110':
            if reg_value[rs1] < reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        # Branch on greater than or equal to, unsigned (bgeu)
        elif funct3 == '111':
            if reg_value[rs1] >= reg_value[rs2]:
                reg_value['PC'] += imm_value * 2

        PC += 1


    #s - type
    elif opcode == '0100011':  # sw
        imm_11_5 = Instruction[25:32]
        rs2 = Instruction[20:25]
        rs1 = Instruction[15:20]
        imm_4_0 = Instruction[7:12]
        imm = sign_extend(imm_11_5 + (imm_4_0 << 5), 12)
        mem_store[reg_value[rs1] + imm] = reg_value[rs2]                
        PC+=1
    
    #u - type
    elif (opcode=='0110111'): #lui
        rd=Instruction[20:25]
        imm = Instruction[0:20]

        reg_value[rd] = PC + sign_extend(imm,12)
        PC += 1

    elif (opcode=='0010111'): #auipc
        imm =Instruction[0:20]

        reg_value[rd] = sign_extend(imm,12)
        PC += 1
    
    #j - type
    elif opcode == '1101111':
        imm = (
            (int(Instruction[0]) << 20) |
            (int(Instruction[1:11], 2) << 1) |
            (int(Instruction[11]) << 11) |
            (int(Instruction[12:20], 2) << 12)
        )
        imm = sign_extend(imm, 21)

        rd = reg[(Instruction[20:25])]

        reg[rd] = pc + 4

        pc = pc + (imm << 1)

    elif opcode == '0000011':  # lw
        rd = Instruction[20:25]
        rs1 = Instruction[15:20]
        imm = Instruction[0:12]
        reg_value[rd] = mem_store[reg_value[rs1] + sign_extend(imm, 12)]

    elif opcode == '0010011':
        rd = Instruction[20:25]
        rs1 = Instruction[15:20]
        imm = Instruction[0:12]
        if funct3 == '000':  # addi
            reg_value[rd] = reg_value[rs1] + sign_extend(imm, 12)
        elif funct3 == '011':  # sltiu
            reg_value[rd] = 1 if unsigned(reg_value[rs1]) < unsigned(sign_extend(imm, 12)) else 0

    elif opcode == '1100111':  # jalr
        rd = Instruction[20:25]
        rs1 = Instruction[15:20]
        imm = Instruction[0:12]
        reg_value[rd] = PC + 4
        PC = (reg_value[rs1] + sign_extend(imm, 12)) & 0xFFFFFFFE  # Make LSB 0
    


PC = 0
halt = 0
cycle = 0    
while(halt == 0):
    Instruction = instructions[PC]
    
    PC_dump()

    ee_execute(Instruction)
    
    pc_update(PC)
    
    reg_dump()
    
mem_dump()
