"""4.1 参考模型：统计非负/负数个数，输出"非负 负"两个 2 位十六进制 + CRLF。"""


def expected(inp: str) -> str:
    toks = inp.split()
    n = int(toks[0], 16) if toks else 0
    vals = [int(t, 16) for t in toks[1:1 + n]]
    vals = [v - 256 if v >= 128 else v for v in vals]      # 当成有符号字节
    pos = sum(1 for v in vals if v >= 0)
    neg = len(vals) - pos
    return f"{pos:02X} {neg:02X}\r\n"


def gen(rng) -> str:
    n = rng.randrange(0, 11)
    vals = []
    for _ in range(n):
        if rng.random() < 0.5:
            vals.append((256 - rng.randrange(1, 128)) & 0xFF)
        else:
            vals.append(rng.choice([0, 0x7F]) if rng.random() < 0.2 else rng.randrange(0, 128))
    if n == 0:
        return "00\n"
    return f"{n:02X} " + " ".join(f"{v:02X}" for v in vals) + "\n"
