"""5.2 参考模型：朴素子串查找，输出 FOUND / NOT FOUND + CRLF。

注意原版演示数据 '1COOCOO$' 里其实**没有** 'COOL'，原版会打印 NOT FOUND，
所以这里用 '1COOCOOL' 才对得上 FOUND 的用例。
"""


def expected(inp: str) -> str:
    parts = inp.split()
    hay = parts[0] if parts else ""
    pat = parts[1] if len(parts) > 1 else ""
    hit = pat != "" and pat in hay
    return ("FOUND" if hit else "NOT FOUND") + "\r\n"


def gen(rng) -> str:
    alphabet = "ABC"
    hay = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 10)))
    if rng.random() < 0.5 and len(hay) >= 2:
        i = rng.randrange(0, len(hay) - 1)
        pat = hay[i:i + rng.randrange(1, 3)]
    else:
        pat = "".join(rng.choice(alphabet) for _ in range(rng.randrange(1, 3)))
    return f"{hay} {pat}\n"
