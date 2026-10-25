"""4.3 参考模型：字符串按 ASCII 升序排序，输出 + CRLF。"""


def expected(inp: str) -> str:
    parts = inp.split()
    word = parts[0] if parts else ""
    return "".join(sorted(word)) + "\r\n"


def gen(rng) -> str:
    alphabet = "abAB9Z0_"
    n = rng.randrange(1, 12)
    return "".join(rng.choice(alphabet) for _ in range(n)) + "\n"
