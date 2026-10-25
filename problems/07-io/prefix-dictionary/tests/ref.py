"""9.2 参考模型：内存版单词字典（忽略大小写、有序插入、去重、前缀查找）。

输入是空白分隔的命令流：1 <word> / 2 <prefix> / 3。
输出与汇编版一致：每条命令一行（CRLF）。
"""

MAXLEN = 30


def run(inp: str) -> list[str]:
    toks = inp.split()
    i = 0
    words: list[str] = []
    out: list[str] = []
    while i < len(toks):
        cmd = toks[i]
        i += 1
        if cmd == "3":
            break
        if cmd == "1":
            w = toks[i] if i < len(toks) else ""
            i += 1
            if len(w) > MAXLEN:
                out.append("TOOLONG")
            elif any(x.upper() == w.upper() for x in words):
                out.append("DUP")
            else:
                words.append(w)
                words.sort(key=str.upper)
                out.append("OK")
        elif cmd == "2":
            p = toks[i] if i < len(toks) else ""
            i += 1
            hits = [w for w in words if w.upper().startswith(p.upper())]
            out.append((" ".join(hits) + " ") if hits else "NONE")
    return out


def expected(inp: str) -> str:
    return "".join(line + "\r\n" for line in run(inp))


def gen(rng) -> str:
    cmds = []
    for _ in range(rng.randrange(1, 8)):
        r = rng.random()
        if r < 0.45:
            w = "".join(rng.choice("abcAB") for _ in range(rng.randrange(1, 5)))
            cmds.append(f"1 {w}")
        elif r < 0.85:
            p = "".join(rng.choice("abAB") for _ in range(rng.randrange(0, 3)))
            cmds.append(f"2 {p}" if p else "2 A")
        else:
            cmds.append("1 " + "x" * 31)
    cmds.append("3")
    return "\n".join(cmds) + "\n"
