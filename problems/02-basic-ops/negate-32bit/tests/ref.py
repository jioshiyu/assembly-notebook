"""1.3 参考模型：32 位数取负（模 2^32），输出 8 位十六进制 + CRLF。"""


def expected(inp: str) -> str:
    lo, hi = (int(t, 16) for t in inp.split()[:2])
    v = (hi << 16) | lo
    return f"{(-v) & 0xFFFFFFFF:08X}\r\n"


def gen(rng) -> str:
    if rng.random() < 0.3:
        lo, hi = rng.choice([(0xFFFB, 0xFFFF), (0, 0), (1, 0), (0, 1), (0xFFFF, 0xFFFF)])
    else:
        lo, hi = rng.randrange(65536), rng.choice([0, 1, 0x7FFF, 0x8000, 0xFFFF,
                                                   rng.randrange(65536)])
    return f"{lo:04X} {hi:04X}\n"
