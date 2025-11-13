import sys

# ----- Opcode mapping (bit 31 is index 0, bit 0 is index 31) -----
opcodes = {
    "0110011": "R-type",   # R-type: {funct7|rs2|rs1|funct3|rd|opcode}
    "0000011": "lw",
    "0010011": "addi",
    "1100111": "jalr",
    "0100011": "sw",
    "1100011": "B-type",   # Branch instructions (beq, bne, etc)
    "1101111": "jal",
    "1110011": "rst",
    "1111111": "halt"
}

# ----- Register encodings -----
# To match expected output, sp (x2) is initialized to 0x17C.
registers = {
    "00000": "zero", 
    "00001": "ra", 
    "00010": "sp", 
    "00011": "gp",
    "00100": "tp", 
    "00101": "t0", 
    "00110": "t1", 
    "00111": "t2",
    "01000": "s0", 
    "01001": "s1", 
    "01010": "a0", 
    "01011": "a1",
    "01100": "a2", 
    "01101": "a3", 
    "01110": "a4", 
    "01111": "a5",
    "10000": "a6", 
    "10001": "a7", 
    "10010": "s2", 
    "10011": "s3",
    "10100": "s4", 
    "10101": "s5", 
    "10110": "s6", 
    "10111": "s7",
    "11000": "s8", 
    "11001": "s9", 
    "11010": "s10", 
    "11011": "s11",
    "11100": "t3", 
    "11101": "t4", 
    "11110": "t5", 
    "11111": "t6"
}

# ----- Data Memory -----
# Allocate memory for addresses 0x00010000 to 0x0001007C (step 4)
datamemory = {}
for addr in range(0x00010000, 0x00010080, 4):
    datamemory[f"{addr:08X}"] = 0

# ----- Register File Initialization -----
# Note: sp (x2) is set to 0x17C.
reg_value = {
    "zero": 0,
    "ra": 0,
    "sp": 0x17C,
    "gp": 0,
    "tp": 0,
    "t0": 0,
    "t1": 0,
    "t2": 0,
    "s0": 0,
    "s1": 0,
    "a0": 0,
    "a1": 0,
    "a2": 0,
    "a3": 0,
    "a4": 0,
    "a5": 0,
    "a6": 0,
    "a7": 0,
    "s2": 0,
    "s3": 0,
    "s4": 0,
    "s5": 0,
    "s6": 0,
    "s7": 0,
    "s8": 0,
    "s9": 0,
    "s10": 0,
    "s11": 0,
    "t3": 0,
    "t4": 0,
    "t5": 0,
    "t6": 0
}

instruction_dict = {}
PC = 0

# ----- Helper Functions -----
def Bin_to_dec(num, bin_length):
    value = int(num, 2)
    if value >= 2 ** (bin_length - 1):
        value -= 2 ** bin_length
    return value

def Dec_to_Bin(number, k):
    if number >= 0:
        s = bin(number)[2:].zfill(k)
    else:
        s = bin((1 << k) + number)[2:]
    return s[-k:]

# ----- Decode Function -----
def decode(bin_code, PC):
    global reg_value, registers, datamemory
    # Opcode is the rightmost 7 bits: indices [25:32]
    opcode = bin_code[25:]
    instruction = opcodes.get(opcode, "unknown")
    if instruction == "R-type":
        PC = R_Type(bin_code, PC)
    elif instruction in ["lw", "addi", "jalr"]:
        PC = I_Type(bin_code, PC)
    elif instruction == "sw":
        PC = S_Type(bin_code, PC)
    elif instruction == "B-type":
        PC = B_Type(bin_code, PC)
    elif instruction == "jal":
        PC = J_Type(bin_code, PC)
    return PC

def R_Type(bin_code, PC):
    global reg_value
    # R-type: funct7 [0:7], rs2 [7:12], rs1 [12:17], funct3 [17:20], rd [20:25]
    func7 = bin_code[0:7]
    rs2   = bin_code[7:12]
    rs1   = bin_code[12:17]
    func3 = bin_code[17:20]
    rd    = bin_code[20:25]
    rs1_val = reg_value[registers[rs1]]
    rs2_val = reg_value[registers[rs2]]
    result = 0
    if func3 == "000":
        if func7 == "0000000":
            result = rs1_val + rs2_val
        elif func7 == "0100000":
            result = rs1_val - rs2_val
    elif func3 == "010" and func7 == "0000000":
        result = 1 if rs1_val < rs2_val else 0
    elif func3 == "101" and func7 == "0000000":
        result = rs1_val >> (rs2_val & 0x1F)
    elif func3 == "110" and func7 == "0000000":
        result = rs1_val | rs2_val
    elif func3 == "111" and func7 == "0000000":
        result = rs1_val & rs2_val
    if registers[rd] != "zero":
        reg_value[registers[rd]] = result
    return PC + 4

def I_Type(bin_code, PC):
    global reg_value, datamemory
    # I-type: imm [0:12] (inst[31:20]), rs1 [12:17] (inst[19:15]),
    # funct3 [17:20] (inst[14:12]), rd [20:25] (inst[11:7])
    imm = bin_code[0:12]
    rs1 = bin_code[12:17]
    func3 = bin_code[17:20]
    rd = bin_code[20:25]
    opcode = opcodes[bin_code[25:]]
    imm_val = Bin_to_dec(imm, 12)
    rs1_val = reg_value[registers[rs1]]
    address = rs1_val + imm_val
    hex_addr = f"{address:08X}"
    if opcode == "lw" and func3 == "010":
        if registers[rd] != "zero":
            reg_value[registers[rd]] = datamemory.get(hex_addr, 0)
    elif opcode == "addi":
        if registers[rd] != "zero":
            reg_value[registers[rd]] = rs1_val + imm_val
    elif opcode == "jalr":
        if registers[rd] != "zero":
            reg_value[registers[rd]] = PC + 4
        return (rs1_val + imm_val) & ~1
    return PC + 4

def S_Type(bin_code, PC):
    global reg_value, datamemory
    # S-type: imm [0:7] (inst[31:25]) concatenated with imm [11:7] (inst[11:7])
    imm = bin_code[0:7] + bin_code[20:25]
    rs2 = bin_code[7:12]
    rs1 = bin_code[12:17]
    imm_val = Bin_to_dec(imm, 12)
    rs1_val = reg_value[registers[rs1]]
    address = rs1_val + imm_val
    hex_addr = f"{address:08X}"
    if hex_addr in datamemory:
        datamemory[hex_addr] = reg_value[registers[rs2]]
    return PC + 4

def B_Type(bin_code, PC):
    global reg_value
    # B-type: immediate formed from:
    # imm[12] = bin_code[0], imm[11] = bin_code[24],
    # imm[10:5] = bin_code[1:7], imm[4:1] = bin_code[20:24]
    imm = bin_code[0] + bin_code[24] + bin_code[1:7] + bin_code[20:24]
    rs2 = bin_code[7:12]
    rs1 = bin_code[12:17]
    func3 = bin_code[17:20]
    imm_val = Bin_to_dec(imm, 12) * 2
    rs1_val = reg_value[registers[rs1]]
    rs2_val = reg_value[registers[rs2]]
    if (func3 == "000" and rs1_val == rs2_val) or (func3 == "001" and rs1_val != rs2_val):
        PC += imm_val - 4
    return PC + 4

def J_Type(bin_code, PC):
    global reg_value
    # J-type: immediate formed from:
    # imm[20] = bin_code[0], imm[10:1] = bin_code[1:11],
    # imm[11] = bin_code[11], imm[19:12] = bin_code[12:20]
    imm = bin_code[0] + bin_code[1:11] + bin_code[11] + bin_code[12:20]
    rd = bin_code[20:25]
    imm_val = Bin_to_dec(imm, 20) * 2
    if registers[rd] != "zero":
        reg_value[registers[rd]] = PC + 4
    return PC + imm_val

def get_state_line(PC):
    parts = [f"0b{Dec_to_Bin(PC,32)}"]
    parts += [f"0b{Dec_to_Bin(reg_value[reg],32)}" for reg in registers.values()]
    return " ".join(parts) + " "

def Read_File(input_file):
    global instruction_dict
    address = 0
    with open(input_file, "r") as file:
        for line in file:
            instr = line.strip()
            if instr:
                instruction_dict[address] = instr
                address += 4

def process_file(input_file, output_file, PC):
    global reg_value, datamemory, instruction_dict
    HALT = "00000000000000000000000001100011"
    Read_File(input_file)
    current_PC = PC
    with open(output_file, "w") as file:
        while current_PC in instruction_dict:
            bin_code = instruction_dict[current_PC]
            if bin_code == HALT:
                file.write(get_state_line(current_PC) + "\n")
                break
            current_PC = decode(bin_code, current_PC)
            file.write(f"0b{Dec_to_Bin(current_PC, 32)} ")
            for reg in registers.values():
                file.write(f"0b{Dec_to_Bin(reg_value[reg], 32)} ")
            file.write("\n")
        for key in sorted(datamemory.keys(), key=lambda x: int(x, 16)):
            file.write(f"0x{key}:0b{Dec_to_Bin(datamemory[key], 32)}\n")

if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    process_file(input_file, output_file, PC=0)
