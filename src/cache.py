

# ==============================================================================
# TRINARY PROCESSOR HARDWARE EXTENSION: DIRECT-MAPPED TERNARY CACHE
# Simulates high-speed SRAM cache slots indexed by balanced ternary keys
# ==============================================================================

class TernaryCache:
    def __init__(self, size=9):
        # Initialize an empty cache structure
        # Key: Ternary Address Slot (-1, 0, 1 mapped indexing)
        self.size = size
        self.cache_slots = {}
        self.hits = 0
        self.misses = 0

    def read(self, address, system_ram):
        """Simulates an architectural cache read cycle."""
        # Hardware slot mapping lookup optimization
        slot_index = address % self.size

        if slot_index in self.cache_slots and self.cache_slots[slot_index]["tag"] == address:
            self.hits += 1
            return self.cache_slots[slot_index]["data"], "HIT"
        else:
            self.misses += 1
            # Cache Miss: Fetch natively from main system memory array
            fetched_data = system_ram.get(address, 0)
            # Allocate and store data inside the high-speed cache line
            self.cache_slots[slot_index] = {"tag": address, "data": fetched_data}
            return fetched_data, "MISS"

    def write(self, address, value, system_ram):
        """Simulates an architectural Write-Through cache cycle."""
        slot_index = address % self.size

        # Write-Through policy: Update cache line and system memory simultaneously
        self.cache_slots[slot_index] = {"tag": address, "data": value}
        system_ram[address] = value


# ==============================================================================
# CACHE VERIFICATION
# ==============================================================================
if __name__ == "__main__":
    print("Testing Ternary Cache Controller...\n")

    # Mocking main system RAM with some seeded values
    mock_ram = {-1: 10, 0: 20, 1: 30}
    cache = TernaryCache()

    # Cycle 1: First read (Expected Cache Miss)
    val, status = cache.read(1, mock_ram)
    print(f"Read Addr 1 : Value={val} | Status={status}")

    # Cycle 2: Second read to same address (Expected Cache Hit)
    val, status = cache.read(1, mock_ram)
    print(f"Read Addr 1 : Value={val} | Status={status}")

    print(f"\nFinal Cache Performance: Hits={cache.hits} | Misses={cache.misses}")
