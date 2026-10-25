"""5.3 参考模型：16 位十六进制 → 5 位十进制（前导零）+ CRLF。"""


def expected(inp: str) -> str:
    v = int(inp.split()[0], 16) if inp.split() else 0
    return f"{v:05d}\r\n"


def gen(rng) -> str:
    choice = rng.random()
    if choice < 0.3:
        v = rng.choice([0, 1, 9, 10, 9999, 10000, 65535, 0x845E])
    else:
        v = rng.randrange(0, 65536)
    return f"{v:04X}\n"
