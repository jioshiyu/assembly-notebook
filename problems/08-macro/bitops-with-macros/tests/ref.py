"""10.1 参考模型：AND/OR/XOR/TEST 四条结果，各带 H 后缀 + CRLF。"""


def expected(inp: str) -> str:
    toks = inp.split()
    a = int(toks[0], 16) if toks else 0
    b = int(toks[1], 16) if len(toks) > 1 else 0
    lines = [
        f"AND={a & b:04X}H",
        f"OR={a | b:04X}H",
        f"XOR={a ^ b:04X}H",
        f"TEST={a:04X}H",       # TEST 不改第一个操作数
    ]
    return "".join(x + "\r\n" for x in lines)


def gen(rng) -> str:
    if rng.random() < 0.3:
        a, b = rng.choice([(0x1234, 0x00FF), (0, 0), (0xFFFF, 0xFFFF), (0xAAAA, 0x5555)])
    else:
        a, b = rng.randrange(65536), rng.randrange(65536)
    return f"{a:04X} {b:04X}\n"
