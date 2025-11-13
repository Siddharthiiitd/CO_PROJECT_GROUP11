import sys
register = {
    'zero': '00000', 'ra': '00001', 'sp': '00010', 'gp': '00011', 'tp': '00100',
    't0': '00101', 't1': '00110', 't2': '00111', 's0': '01000', 'fp': '01000',
    's1': '01001', 'a0': '01010', 'a1': '01011', 'a2': '01100', 'a3': '01101',
    'a4': '01110', 'a5': '01111', 'a6': '10000', 'a7': '10001', 's2': '10010',
    's3': '10011', 's4': '10100', 's5': '10101', 's6': '10110', 's7': '10111',
    's8': '11000', 's9': '11001', 's10': '11010', 's11': '11011', 't3': '11100',
    't4': '11101', 't5': '11110', 't6': '11111'
}

def Bin_from_Imm(imm, width=12):    #convert immediate to binary
    if imm >= 0:
        return format(imm, f'0{width}b')[-width:]
    else:
        return format((1 << width) + imm, f'0{width}b')[-width:]

def generate_r_type(funct7, funct3, rd, rs1, rs2, register, line_no):
    try:
        return f"{funct7}{register[rs2]}{register[rs1]}{funct3}{register[rd]}0110011"
    except KeyError as e:
        return f"RegisterNotFound in line {line_no}: {e}"

def generate_i_type(opcode, funct3, rd, rs1, imm, register, line_no):
    try:
        imm_bin = Bin_from_Imm(imm)
        return f"{imm_bin}{register[rs1]}{funct3}{register[rd]}{opcode}"
    except KeyError as e:
        return f"RegisterNotFound in line {line_no}: {e}"

def generate_s_type(opcode, funct3, rs1, rs2, imm, register, line_no):
    try:
        imm_bin = Bin_from_Imm(imm)
        return f"{imm_bin[0:7]}{register[rs2]}{register[rs1]}{funct3}{imm_bin[7:12]}{opcode}"
    except KeyError as e:
        return f"RegisterNotFound in line {line_no}: {e}"

def generate_b_type(opcode, funct3, rs1, rs2, imm, register, line_no):
    try:
        imm_bin = Bin_from_Imm(imm, 13)
        return f"{imm_bin[0]}{imm_bin[2:8]}{register[rs2]}{register[rs1]}{funct3}{imm_bin[8:12]}{imm_bin[1]}1100011"
    except KeyError as e:
        return f"RegisterNotFound in line {line_no}: {e}"

def generate_j_type(opcode, rd, imm, register, line_no):
    try:
        imm_bin = Bin_from_Imm(imm, 20)
        return f"{imm_bin[0]}{imm_bin[10:20]}{imm_bin[9]}{imm_bin[1:9]}{register[rd]}{opcode}"
    except KeyError as e:
        return f"RegisterNotFound in line {line_no}: {e}"

# Instruction Definitions
def Add(rd, rs1, rs2, register, line_no):
    return generate_r_type("0000000", "000", rd, rs1, rs2, register, line_no)

def Sub(rd, rs1, rs2, register, line_no):
    return generate_r_type("0100000", "000", rd, rs1, rs2, register, line_no)

def Slt(rd, rs1, rs2, register, line_no):
    return generate_r_type("0000000", "010", rd, rs1, rs2, register, line_no)

def Srl(rd, rs1, rs2, register, line_no):
    return generate_r_type("0000000", "101", rd, rs1, rs2, register, line_no)

def Or(rd, rs1, rs2, register, line_no):
    return generate_r_type("0000000", "110", rd, rs1, rs2, register, line_no)

def Addi(rd, rs1, imm, register, line_no):
    return generate_i_type("0010011", "000", rd, rs1, imm, register, line_no)

def Jalr(rd, rs1, imm, register, line_no):
    return generate_i_type("1100111", "000", rd, rs1, imm, register, line_no)

def Lw(rd, rs1, imm, register, line_no):
    return generate_i_type("0000011", "010", rd, rs1, imm, register, line_no)

def Sw(rs2, rs1, imm, register, line_no):
    return generate_s_type("0100011", "010", rs1, rs2, imm, register, line_no)

def Beq(rs1, rs2, imm, register, line_no):
    return generate_b_type("1100011", "000", rs1, rs2, imm, register, line_no)

def Bne(rs1, rs2, imm, register, line_no):
    return generate_b_type("1100011", "001", rs1, rs2, imm, register, line_no)

def Jal(rd, imm, register, line_no):
    return generate_j_type("1101111", rd, imm, register, line_no)

def process_memory_op(operand):     #for memory operations like lw/sw
    
    if '(' not in operand or ')' not in operand:
        raise ValueError("Invalid memory operation format")
    parts = operand.split('(')
    offset = parts[0].strip()
    register = parts[1].rstrip(')').strip()
    return int(offset), register

def process_labels(lines):    #Process labels from assembly code
    
    labels = {}
    processed_lines = []
    current_line = 0
    
    for line in lines:
        if not line:
            continue
            
        if ':' in line[0]:
            parts = line[0].split(':')
            label_name = parts[0]
            labels[label_name] = current_line
            if len(parts) > 1 and parts[1]:
                line[0] = parts[1]
                processed_lines.append(line)
                current_line += 1
            elif len(line) > 1:
                processed_lines.append(line[1:])
                current_line += 1
            continue
            
        processed_lines.append(line)
        current_line += 1
    
    return labels, processed_lines

def caller(instruction, operands, line_no, labels):
    
    try:
        instruction = instruction.lower()
        if instruction == "add":
            rd, rs1, rs2 = [op.strip() for op in operands]
            return Add(rd, rs1, rs2, register, line_no)
        elif instruction == "sub":
            rd, rs1, rs2 = [op.strip() for op in operands]
            return Sub(rd, rs1, rs2, register, line_no)
        elif instruction == "jal":
            rd, imm = [op.strip() for op in operands]
            return Jal(rd, int(imm), register, line_no)
        elif instruction == "slt":
            rd, rs1, rs2 = [op.strip() for op in operands]
            return Slt(rd, rs1, rs2, register, line_no)
        elif instruction == "srl":
            rd, rs1, rs2 = [op.strip() for op in operands]
            return Srl(rd, rs1, rs2, register, line_no)
        elif instruction == "or":
            rd, rs1, rs2 = [op.strip() for op in operands]
            return Or(rd, rs1, rs2, register, line_no)
        elif instruction == "addi":
            rd, rs1, imm = [op.strip() for op in operands]
            return Addi(rd, rs1, int(imm), register, line_no)
        elif instruction == "jalr":
            rd, rs1, imm = [op.strip() for op in operands]
            return Jalr(rd, rs1, int(imm), register, line_no)
        elif instruction == "lw":
            rd, mem_op = [op.strip() for op in operands]
            offset, rs1 = process_memory_op(mem_op)
            return Lw(rd, rs1, offset, register, line_no)
        elif instruction == "sw":
            rs2, mem_op = [op.strip() for op in operands]
            offset, rs1 = process_memory_op(mem_op)
            return Sw(rs2, rs1, offset, register, line_no)
        elif instruction == "beq":
            rs1, rs2, offset = [op.strip() for op in operands]
            offset = int(offset) if offset.isdigit() or offset[0] == '-' else (labels[offset] - line_no) * 4
            return Beq(rs1, rs2, offset, register, line_no)
        elif instruction == "bne":
            rs1, rs2, offset = [op.strip() for op in operands]
            offset = int(offset) if offset.isdigit() or offset[0] == '-' else (labels[offset] - line_no) * 4
            return Bne(rs1, rs2, offset, register, line_no)
    except Exception as e:
        return f"Error in line {line_no}: {str(e)}"

def import_file(input_file):   #Read input file
    
    try:
        with open(input_file, 'r') as f:
            lines = f.readlines()
        processed_lines = []
        for line in lines:
            line = line.split('#', 1)[0].strip()
            if not line:
                continue
            line = line.replace(',', ' ')
            line = ' '.join(line.split())
            tokens = line.split()
            if tokens:
                processed_lines.append(tokens)
        return processed_lines
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

def write_output(output_filename, binary_data): #Write binary into output file
    
    try:
        with open(output_filename, 'w') as f:
            for instr in binary_data:
                if len(instr) == 32 and all(bit in '01' for bit in instr):
                    f.write(instr + '\n')
                else:
                    print(f"Error: {instr}")
    except Exception as e:
        print(f"Error writing to file: {e}")

def run_assembler(input_filename, output_filename): # Main function to run the assembler
    
    try:
        lines = import_file(input_filename)
        if not lines:
            print("No valid instructions found in input file")
            return
        
        labels, processed_lines = process_labels(lines)
        binary_data = []
        
        for idx, line in enumerate(processed_lines):
            if not line:
                continue
            instruction = line[0]
            operands = line[1:] if len(line) > 1 else []
            result = caller(instruction, operands, idx, labels)
            binary_data.append(result)
        
        write_output(output_filename, binary_data)
        
    except Exception as e:
        print(f"Error during assembly: {e}")

if len(sys.argv) > 2:
    input_filename = sys.argv[1]
    output_filename = sys.argv[2]
elif len(sys.argv) > 1:
    input_filename = sys.argv[1]
    output_filename = "output.txt"
else:
    input_filename = "test.txt"        # input filename
    output_filename = "output.txt"     # output filename

import os  # For checking file existence
print(f"Current working directory: {os.getcwd()}")
print(f"Looking for input file: {input_filename}")
if not os.path.exists(input_filename):
    print(f"Error: The file '{input_filename}' does not exist in the specified directory.")
else:
    try:
        run_assembler(input_filename, output_filename)
        print(f"Assembly completed. Output written to {output_filename}")
    except Exception as e:
        print(f"Error: {e}")