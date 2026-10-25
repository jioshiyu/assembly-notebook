"""7.2 参考模型：X^N 按 2^16 取模，十进制输出 + CRLF。"""


def expected(inp: str) -> str:
    toks = inp.split()
    x = int(toks[0], 16) if toks else 0
    n = int(toks[1], 16) if len(toks) > 1 else 0
    return f"{pow(x, n, 1 << 16)}\r\n"


def gen(rng) -> str:
    if rng.random() < 0.4:
        x, n = rng.choice([(3, 5), (0, 0), (2, 16), (1, 255), (255, 2), (10, 4)])
    else:
        x = rng.randrange(256)
        n = rng.randrange(0, 8)
    return f"{x:02X} {n:02X}\n"
