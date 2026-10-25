"""6.3 参考模型：删除从第 N 个字符（1 基）起的 M 个字符；M 超长时截断到串尾。"""


def expected(inp: str) -> str:
    toks = inp.split()
    s = toks[0] if toks else ""
    n = int(toks[1], 16) if len(toks) > 1 else 0
    m = int(toks[2], 16) if len(toks) > 2 else 0
    if n == 0 or n > len(s):
        return s + "\r\n"
    m = min(m, len(s) - n + 1)
    return (s[:n - 1] + s[n - 1 + m:]) + "\r\n"


def gen(rng) -> str:
    alphabet = "ABCDEFGH"
    n = rng.randrange(1, 10)
    s = "".join(rng.choice(alphabet) for _ in range(n))
    start = rng.randrange(0, 12)
    count = rng.randrange(0, 8)
    return f"{s} {start:02X} {count:02X}\n"
