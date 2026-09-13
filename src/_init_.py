
# ==============================================================================
# TRINARY PROCESSOR HARDWARE EXTENSION: ASSEMBLY CODE TEXT PARSER
# Converts readable assembly instructions into executable hardware tuples
# ==============================================================================

class TernaryAssemblyParser:
    @staticmethod
    def parse_line(line):
        """Parses a single line of ternary assembly text."""
        # Strip comments and whitespace
        clean_line = line.split(";")[0].strip()
        if not clean_line:
            return "NOP"

        # Split instruction into opcode and operands
        parts = clean_line.replace(",", " ").split()
        op = parts[0].upper()

        if op == "NOP":
            return "NOP"

        # Handle Control Flow: BRZ [Target_PC] [Register_To_Test]
        if op == "BRZ":
            target_pc = int(parts[1])
            reg_test = int(parts[2])
            return (op, target_pc, reg_test, 0)

        # Handle Arithmetic: ADD/MUL/INV [Dest_Reg] [Src_A] [Src_B]
        dest = int(parts[1])
        src_a = int(parts[2])
        src_b = int(parts[3]) if len(parts) > 3 else 0

        return (op, dest, src_a, src_b)

    @classmethod
    def parse_program(cls, source_text):
        """Converts an entire assembly program into a pipeline-ready array."""
        program = []
        for line in source_text.strip().split("\n"):
            parsed = cls.parse_line(line)
            if parsed != "NOP" or line.strip().startswith("NOP"):
                program.append(parsed)
        return program


# ==============================================================================
# PARSER VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    # Sample readable text file representation
    assembly_code = """
    ADD  1,  1,  1  ; Add contents of R(1) and R(1), store in R(1)
    INV -1,  1     ; Invert R(1), store in R(-1)
    BRZ  4,  0     ; If R(0) is neutral 0, branch directly to line 4
    MUL  0, -1, -1  ; Line 4 (Target): Multiply R(-1) by R(-1), store in R(0)
    """

    executable_array = TernaryAssemblyParser.parse_program(assembly_code)
    print("Compiled Ternary Hardware Instruction Set:")
    for idx, inst in enumerate(executable_array):
        print(f" Address {idx:02d}: {inst}")
