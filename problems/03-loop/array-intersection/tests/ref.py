"""4.2 参考模型：按 A 的顺序求交集，输出每个元素 2 位十六进制 + 空格；空则 NONE。"""


def _parse(inp):
    toks = inp.split()
    i = 0
    n = int(toks[i], 16)
    i += 1
    a = [int(t, 16) for t in toks[i:i + n]]
    i += n
    m = int(toks[i], 16)
    i += 1
    b = [int(t, 16) for t in toks[i:i + m]]
    return a, b


def expected(inp: str) -> str:
    a, b = _parse(inp)
    common = [x for x in a if x in b]
    body = "".join(f"{x:02X} " for x in common) if common else "NONE"
    return body + "\r\n"


def gen(rng) -> str:
    n = rng.randrange(0, 6)
    m = rng.randrange(0, 6)
    a = [rng.randrange(0x41, 0x48) for _ in range(n)]
    b = [rng.randrange(0x41, 0x48) for _ in range(m)]
    a_s = " ".join(f"{x:02X}" for x in a)
    b_s = " ".join(f"{x:02X}" for x in b)
    return f"{n:02X} {a_s} {m:02X} {b_s}\n".replace("  ", " ")
