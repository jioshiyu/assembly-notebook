"""5.1 参考模型：两个词直接拼接，输出 + CRLF。"""


def expected(inp: str) -> str:
    parts = inp.split()
    a = parts[0] if parts else ""
    b = parts[1] if len(parts) > 1 else ""
    return a + b + "\r\n"


def gen(rng) -> str:
    alphabet = "ABCXYZ0123"
    a = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 9)))
    b = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 9)))
    return f"{a} {b}\n"
