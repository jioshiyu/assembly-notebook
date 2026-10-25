"""6.2 参考模型：16 位值 → 4 位十六进制 + 'H' + CRLF。"""


def expected(inp: str) -> str:
    v = int(inp.split()[0], 16) if inp.split() else 0
    return f"{v:04X}H\r\n"


def gen(rng) -> str:
    if rng.random() < 0.3:
        v = rng.choice([0, 1, 9, 10, 15, 16, 0x845E, 0xFFFF])
    else:
        v = rng.randrange(0, 65536)
    return f"{v:04X}\n"
