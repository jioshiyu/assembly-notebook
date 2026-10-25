"""6.1.1 参考模型：原样回显一个词 + CRLF（对应"打印到 '!' 为止"的可测版本）。"""


def expected(inp: str) -> str:
    parts = inp.split()
    return (parts[0] if parts else "") + "\r\n"


def gen(rng) -> str:
    alphabet = "ABCXYZ_0123"
    n = rng.randrange(1, 16)
    return "".join(rng.choice(alphabet) for _ in range(n)) + "\n"
