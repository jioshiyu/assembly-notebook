"""0.x 参考模型：四个传送类练习的结果。

输入：I（查表下标）、A（8 位加法输入）
输出：COPY / PUSH_POP / XLAT / ADD+标志
"""

TABLE = [0x18, 0x34, 0x05, 0x06, 0x09, 0x0A, 0x0C, 0x11, 0x12]
DATA = [0x12, 0x34, 0x56, 0x78]


def expected(inp: str) -> str:
    toks = inp.split()
    idx = int(toks[0], 16) if toks else 0
    num = int(toks[1], 16) if len(toks) > 1 else 0
    xl = TABLE[idx % len(TABLE)]
    total = num + 1
    s = total & 0xFF
    cf = 1 if total > 0xFF else 0
    of = 1 if num == 0x7F else 0
    sf = 1 if s & 0x80 else 0
    copy = "".join(f"{b:02X}" for b in DATA)
    return (f"COPY={copy}\r\n"
            f"PUSH_POP=0435\r\n"
            f"XLAT={xl:02X}\r\n"
            f"ADD={s:02X} CF={cf:02X} OF={of:02X} SF={sf:02X}\r\n")


def gen(rng) -> str:
    idx = rng.randrange(0, 12)
    num = rng.choice([0, 1, 0x7E, 0x7F, 0x80, 0xFE, 0xFF]) if rng.random() < 0.6 \
        else rng.randrange(256)
    return f"{idx:02X} {num:02X}\n"
