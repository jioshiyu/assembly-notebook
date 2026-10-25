"""1.2 参考模型：AL=a*b 取低 8 位，AAM 拆成 (商, 余)，输出 AH:AL 的 4 位十六进制。"""


def expected(inp: str) -> str:
    a, b = (int(t, 16) for t in inp.split()[:2])
    prod_low = (a * b) & 0xFF
    q, r = divmod(prod_low, 10)
    return f"{q * 256 + r:04X}\r\n"


def gen(rng) -> str:
    if rng.random() < 0.3:
        a, b = rng.choice([(8, 7), (0, 0), (15, 15), (13, 13), (16, 16)])
    else:
        a, b = rng.randrange(256), rng.randrange(256)
    return f"{a:02X} {b:02X}\n"
