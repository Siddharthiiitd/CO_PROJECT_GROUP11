
# RISC-V Assembler and Simulator

This project is a two-stage 32-bit RISC-V processor pipeline, featuring a Python-based Assembler and a functional Simulator. It was developed as part of a Computer Organization (CO) course.

- **Assembler (`co_assembler.py`)**: Converts a text file of RISC-V assembly instructions into 32-bit binary machine code.  
- **Simulator (`Simulator.py`)**: Executes the binary machine code, simulating the RISC-V register file and data memory, and produces a trace of the execution.

## Features

This project supports a subset of the RV32I (RISC-V 32-bit Integer) instruction set.

### Supported Instructions

| Type   | Instruction | Example Assembly         |
|--------|-------------|--------------------------|
| R-type | `add`       | `add s0, s1, s2`         |
|        | `sub`       | `sub t0, t1, t2`         |
|        | `slt`       | `slt a0, s1, t0`         |
|        | `srl`       | `srl t1, t1, t2`         |
|        | `or`        | `or a0, a0, a1`          |
|        | `and`       | `and s2, s2, s3`         |
| I-type | `addi`      | `addi sp, sp, -8`        |
|        | `lw`        | `lw ra, 4(sp)`           |
|        | `jalr`      | `jalr zero, ra, 0`       |
| S-type | `sw`        | `sw s0, 0(sp)`           |
| B-type | `beq`       | `beq t0, t1, loop`       |
|        | `bne`       | `bne a0, zero, end`      |
| J-type | `jal`       | `jal ra, function`       |

## Assembler Features

- **Label Resolution**: Correctly calculates and encodes branch/jump offsets for symbolic labels (e.g., `loop:`, `bne t0, zero, loop`).
- **Memory Syntax**: Parses the `offset(register)` syntax for `lw` and `sw` instructions.
- **Comment Stripping**: Ignores comments (anything after a `#`) in the assembly file.
- **Immediate Conversion**: Handles positive and negative decimal immediates and converts them to the correct two's complement binary representation.

## Simulator Features

- **Register File**: Simulates all 32 RV32I general-purpose registers (`zero`, `ra`, `sp`, `t0`, etc.).
  - The `zero` register is hardwired to 0.
  - The `sp` (stack pointer) is initialized to `0x17C`.
- **Data Memory**: Simulates a data memory region from `0x00010000` to `0x00010080`.
- **Execution Trace**: Generates an output file that logs the state of the Program Counter (PC) and all 32 registers after each instruction is executed.
- **Memory Dump**: Appends the final state of all modified data memory locations to the end of the trace file.
- **Halt Detection**: The simulator halts execution when it encounters a specific instruction: `beq zero, zero, 0` (binary: `00000000000000000000000001100011`).

## How to Use

Follow these steps to assemble and run a RISC-V program.

### Prerequisites

- Python 3.x

### Step 1: Write Assembly Code

Create a `.txt` file (e.g., `fibonacci.asm`) with your RISC-V assembly instructions.

Example: `fibonacci.asm`

```assembly
# Calculates the 5th Fibonacci number (n=5)
# n is in a0, result will be in a1

    addi a0, zero, 5   # n = 5
    addi a1, zero, 0   # f(n), our result
    addi t0, zero, 0   # f(n-2)
    addi t1, zero, 1   # f(n-1)
    addi t2, zero, 1   # counter i = 1

loop:
    beq t2, a0, end    # if i == n, goto end
    add a1, t0, t1     # f(n) = f(n-2) + f(n-1)
    add t0, t1, zero   # f(n-2) = f(n-1)
    add t1, a1, zero   # f(n-1) = f(n)
    addi t2, t2, 1     # i = i + 1
    jal zero, loop     # goto loop

end:
    # The result (f(5) = 5) is now in a1
    # Halt the program
    beq zero, zero, 0
```

### Step 2: Assemble the Code

Run the `co_assembler.py` script to convert your assembly file into machine code.

**Syntax:**

```bash
python co_assembler.py <input_assembly_file> <output_binary_file>
```

**Example:**

```bash
python co_assembler.py fibonacci.asm machine_code.txt
```

This will create `machine_code.txt` containing the 32-bit binary instructions, one per line.

### Step 3: Simulate the Machine Code

Run the `Simulator.py` script to execute the binary file.

**Syntax:**

```bash
python Simulator.py <input_binary_file> <output_trace_file>
```

**Example:**

```bash
python Simulator.py machine_code.txt simulation_output.txt
```

### Step 4: Check the Output

Open `simulation_output.txt` to see the results.

## Project File Descriptions

- `co_assembler.py`: The Python script for the Assembler. It parses assembly text and outputs binary machine code.
- `Simulator.py`: The Python script for the Simulator. It reads binary machine code, executes it, and outputs a state trace.

---

## Contributions
- Siddharth Verma
- Vansh Singh
- Snehil Modi
- Smridhi Tandon
