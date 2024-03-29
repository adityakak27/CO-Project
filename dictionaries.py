#define instruction names
instructions_Dictionary = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and",
                      "lw", "addi", "sltiu", "jalr", "sw", "beq", "bne", "blt",
                      "bge", "bltu", "bgeu", "lui", "auipc", "jal", "mul", "rst",
                      "halt", "rvrs", "div", "rem"]


#modified registers dictionary with their address values
registers_Dictionary = {"zero":"00000", "ra":"00001", "sp":"00010", "tp":"00100", "gp":"00011", "t0":"00101", "t1":"00110", "t2":"00111", 
    "fp":"01000", "s0":"01000", "s1":"01001", "a0":"01010", "a1":"01011", "a2":"01100", "a3":"01101", "a4":"01110", "a5":"01111", "a6":"10000", 
    "a7":"10001", "s2":"10010", "s3":"10011", "s4":"10100", "s5":"10101", "s6":"10110", 
    "s7":"10111", "s8":"11000", "s9":"11001", "s10":"11010", "s11":"11011", "t3":"11100", "t4":"11101", "t5":"11110", "t6":"11111" }

#define dictionaries for opcode and funct3 codes
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
    "div": "0110011", "rem": "0110011",  
}

functions_dict = {
    "add": "000", "sub": "000", "sll": "001",
    "slt": "010", "sltu": "011", "xor": "100",
    "srl": "101", "or": "110", "and": "111",
    "lw": "010", "addi": "000", "sltiu": "011",
    "jalr": "000", "sw": "010", "beq": "000",
    "bne": "001", "blt": "100", "bge": "101",
    "bltu": "110", "bgeu": "111", "mul": "000",
    "rst": "000", "halt": "001", "rvrs": "010",
    "div": "100", "rem": "110",  
}











