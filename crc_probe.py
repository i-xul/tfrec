POLY = 0x04C11DB7

raw = bytes.fromhex(
    "4b 2d d4 2b 24 18 36 25 38 8a 34 c0 "
    "80 a7 00 ef 2e 27 30 00 ee 2e 27 2f "
    "03 09 13 17 20 2a 01 01 01 01 01 01 "
    "c0 99 c2 26 00 90 89 10"
)

plen = raw[4]
payload = raw[4:plen]
expected = int.from_bytes(raw[plen:plen + 4], "big")

def crc32(data, init):
    crc = init
    for byte in data:
        crc ^= byte << 24
        for _ in range(8):
            crc = ((crc << 1) ^ (POLY if crc & 0x80000000 else 0)) & 0xFFFFFFFF
    return crc

# CRC:n alkutilan vaikutus lopputulokseen on lineaarinen.
base = crc32(payload, 0)
target = expected ^ base

columns = [crc32(payload, 1 << i) ^ base for i in range(32)]

basis = {}
for i, col in enumerate(columns):
    v, mask = col, 1 << i
    while v:
        pivot = v.bit_length() - 1
        if pivot not in basis:
            basis[pivot] = (v, mask)
            break
        bv, bm = basis[pivot]
        v ^= bv
        mask ^= bm

value = target
init = 0

while value:
    pivot = value.bit_length() - 1
    if pivot not in basis:
        raise RuntimeError("CRC-alkuarvoa ei voitu ratkaista")
    bv, bm = basis[pivot]
    value ^= bv
    init ^= bm

print(f"Sensor type: 0x{raw[5]:02x}")
print(f"Payload length: {plen}")
print(f"Expected CRC: 0x{expected:08x}")
print(f"Candidate init: 0x{init:08x}")
print(f"Calculated CRC: 0x{crc32(payload, init):08x}")
print(f"Match: {crc32(payload, init) == expected}")
