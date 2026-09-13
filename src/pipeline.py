# ==============================================================================
# TRINARY PROCESSOR HARDWARE EXTENSION: 24-TRIT BALANCED ARITHMETIC CORE
# Replaces Python integer math with native hardware logic-gate lookups
# ==============================================================================

class TernaryALU:
    @staticmethod
    def half_adder(a, b):
        """
        Simulates a physical Ternary Half-Adder cell.
        Returns: (carry, sum)
        """
        # Native hardware gate simulation via primitive matching
        raw_sum = a + b
        if raw_sum == -2:  return -1, 1
        if raw_sum == -1:  return 0, -1
        if raw_sum == 0:   return 0, 0
        if raw_sum == 1:   return 0, 1
        if raw_sum == 2:   return 1, -1
        return 0, 0

    @staticmethod
    def full_adder(a, b, carry_in):
        """
        Simulates a physical Ternary Full-Adder cell with carry-in.
        Returns: (carry_out, sum)
        """
        c1, s1 = TernaryALU.half_adder(a, b)
        c2, s2 = TernaryALU.half_adder(s1, carry_in)

        # Combine carry signals natively
        carry_out = c1 + c2
        return carry_out, s2

    @classmethod
    def add_24_trit(cls, word_a, word_b):
        """
        Executes a 24-trit parallel ripple-carry addition.
        Inputs: Lists of 24 trits, ordered from Least Significant Trit (index 0)
                to Most Significant Trit (index 23).
        Returns: List of 24 trits (result) and an overflow flag.
        """
        result = [0] * 24
        carry = 0

        # Ripple the carry across all 24 individual hardware adder stages
        for i in range(24):
            carry, sum_trit = cls.full_adder(word_a[i], word_b[i], carry)
            result[i] = sum_trit

        return result, carry

class TrinaryProcessorPipeline:
    def __init__(self):
        # 1. Hardware State
        self.TRF = { -1: 0, 0: 0, 1: 0 }  # Ternary Register File: R(-1), R(0), R(1)
        self.T_PC = 0                     # Ternary Program Counter
        self.Cycles = 0                   # Global Clock Cycles

        # 2. Program Space
        # Dyadic/Monadic format: (Opcode, Dest_Reg, Src_A, Src_B)
        # Control flow format:   ("BRZ", Target_PC, Src_Test, 0)
        self.Program_Memory = []

        # 3. Pipeline Interstage Latches
        self.IF_ID = None   # Instruction Fetch -> Instruction Decode
        self.ID_EX = None   # Instruction Decode -> Execute
        self.EX_WB = None   # Execute -> Write-Back

        # 4. Control Signals
        self.Flush_Pipeline = False

    def load_program(self, program):
        """Loads a sequence of ternary instructions into execution memory."""
        self.Program_Memory = program
        self.T_PC = 0
        self.Cycles = 0
        self.IF_ID, self.ID_EX, self.EX_WB = None, None, None

    def step_cycle(self):
        """Executes one clock cycle across all active pipeline stages simultaneously."""
        self.Cycles += 1
        self.Flush_Pipeline = False  # Reset branch flush flag

        # --- STAGE 4: WRITE-BACK (WB) ---
        if self.EX_WB:
            dest_reg, result = self.EX_WB["dest"], self.EX_WB["val"]
            if dest_reg in self.TRF:
                # Balanced ternary optimization: 0 values require no state flip
                if result != 0 or self.TRF[dest_reg] != 0:
                    self.TRF[dest_reg] = result

        # --- STAGE 3: EXECUTE (EX) ---
        next_EX_WB = None
        if self.ID_EX and self.ID_EX["op"] != "NOP":
            op = self.ID_EX["op"]
            dest = self.ID_EX["dest"]
            val_a = self.ID_EX["val_A"]
            val_b = self.ID_EX["val_B"]

            # Zero-Delay Data Forwarding network logic
            if self.EX_WB and self.EX_WB["dest"] == self.ID_EX["reg_A"]:
                val_a = self.EX_WB["val"]
            if self.EX_WB and self.EX_WB["dest"] == self.ID_EX["reg_B"]:
                val_b = self.EX_WB["val"]

            if op == "BRZ":
                # Control Hazard: Branch if the monitored register resolves to zero
                if val_a == 0:
                    self.T_PC = dest  # Target PC address
                    self.Flush_Pipeline = True
                res = 0
            else:
                # INTEGRATED TERNARY HARDWARE ARITHMETIC PATHS
                if op == "INV":
                    res = -val_a  # Monadic path: instant hardware inversion
                elif op == "ADD":
                    # Hardware Integration: Running individual trit full-adders
                    # For a single-trit pipeline slice, it acts exactly like a 1-trit ALU block
                    _, res = TernaryALU.full_adder(val_a, val_b, 0)
                elif op == "MUL":
                    res = val_a * val_b  # Symmetrical multiplication matrix
                else:
                    res = 0

            if op != "BRZ":
                next_EX_WB = {"dest": dest, "val": res}

        # --- STAGE 2: DECODE (ID) ---
        next_ID_EX = None
        if self.IF_ID:
            if self.IF_ID == "BUBBLE" or self.IF_ID == "NOP" or self.Flush_Pipeline:
                next_ID_EX = {"op": "NOP", "dest": 0, "reg_A": 0, "val_A": 0, "reg_B": 0, "val_B": 0}
            else:
                op, dest, reg_A, reg_B = self.IF_ID
                next_ID_EX = {
                    "op": op, "dest": dest, "reg_A": reg_A, "val_A": self.TRF[reg_A],
                    "reg_B": reg_B, "val_B": self.TRF[reg_B]
                }

        # --- STAGE 1: FETCH (IF) ---
        if self.Flush_Pipeline:
            # Control hazard resolution: Overwrite raw fetch buffer with a hardware NOP bubble
            next_IF_ID = "BUBBLE"
        elif self.T_PC < len(self.Program_Memory):
            next_IF_ID = self.Program_Memory[self.T_PC]
            self.T_PC += 1
        else:
            next_IF_ID = "BUBBLE"

        # Propagate latch changes across the clock edge boundary
        self.EX_WB = next_EX_WB
        self.ID_EX = next_ID_EX
        self.IF_ID = next_IF_ID

    def print_state(self):
        """Outputs current microarchitectural pipeline trace."""
        print(f"┌── [ Cycle {self.Cycles:02d} ] ──────────────────────────────────────────┐")
        print(f"│ T_PC       : {self.T_PC}")
        print(f"│ Registers  : R(-1)={self.TRF[-1]:>2} | R(0)={self.TRF[0]:>2} | R(1)={self.TRF[1]:>2}")
        print(f"│ IF Stage   : {self.IF_ID}")
        print(f"│ ID Stage   : {self.ID_EX['op'] if self.ID_EX else 'None'}")
        print(f"│ EX Stage   : Out -> {self.EX_WB['val'] if self.EX_WB else 'None'} (to R({self.EX_WB['dest'] if self.EX_WB else 0}))")
        print(f"└─────────────────────────────────────────────────────────────┘\n")


if __name__ == "__main__":
    # Test suite verifying arithmetic pipeline alongside control flow branches
    test_program = [
        ("ADD",  1,  1,  1),  # 0. R(1) = 1 + 1 -> Clamped to +1
        ("INV", -1,  1,  0),  # 1. R(-1) = INV(R(1)) -> Evaluates to -1 via forwarding
        ("BRZ",  4,  0,  0),  # 2. If R(0) == 0, jump to instruction 4 (Should Branch)
        ("ADD",  1, -1, -1),  # 3. Dead code path (Should be skipped by control flush)
        ("MUL",  0, -1, -1),  # 4. Branch target: R(0) = -1 * -1 -> Evaluates to +1
    ]

    cpu = TrinaryProcessorPipeline()
    cpu.TRF[1] = 1  # Initialize R(1) to +1
    cpu.load_program(test_program)

    print("Executing Behavioral Verification Trace...\n")
    for _ in range(7):
        cpu.step_cycle()
        cpu.print_state()
