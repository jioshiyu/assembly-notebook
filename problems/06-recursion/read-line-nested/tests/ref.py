"""7.1 参考模型：整行回显（保留空格）+ CRLF。"""


def expected(inp: str) -> str:
    line = inp.split("\n")[0].rstrip("\r")
    return line + "\r\n"


def gen(rng) -> str:
    alphabet = "ABCXYZ _0123"
    n = rng.randrange(1, 20)
    return "".join(rng.choice(alphabet) for _ in range(n)).strip() + "\n"
