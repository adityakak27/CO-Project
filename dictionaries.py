#Define instruction and register names
instructions_Dictionary = ["add", "sub", "sll", "slt", "sltu", "xor", "srl", "or", "and",
                      "lw", "addi", "sltiu", "jalr", "sw", "beq", "bne", "blt",
                      "bge", "bltu", "bgeu", "lui", "auipc", "jal", "mul", "rst",
                      "halt", "rvrs", "div", "rem"]

registers_Dictionary = ["x" + str(i) for i in range(32)]

#Define dictionaries for opcode and funct3 encoding
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
