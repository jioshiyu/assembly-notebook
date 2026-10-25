"""10.2 参考模型：六种寻址方式都把同一个值写进 BUF，第 1 种是立即数 1234H。"""


def expected(inp: str) -> str:
    toks = inp.split()
    v = int(toks[0], 16) if toks else 0
    lines = [
        "1 IMMEDIATE=1234",
        f"2 REGISTER={v:04X}",
        f"3 DIRECT={v:04X}",
        f"4 INDIRECT={v:04X}",
        f"5 RELATIVE={v:04X}",
        f"6 BASED_INDEXED={v:04X}",
    ]
    return "".join(x + "\r\n" for x in lines)


def gen(rng) -> str:
    if rng.random() < 0.3:
        v = rng.choice([0, 1, 0xFFFF, 0x1234, 0x8000])
    else:
        v = rng.randrange(65536)
    return f"{v:04X}\n"
