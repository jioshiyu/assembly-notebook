"""9.2 参考模型：内存版单词字典 + **磁盘版（DICT.TXT 固定 32 字节记录）**。

原版是磁盘字典（DICT.TXT + 临时文件 + 句柄）；这里的重写版把记录固定成 32 字节
（词 + 0 填充），插入后整表覆盖写回，所以除了 stdout 还能对拍**文件内容**。
"""

MAXLEN = 30
RECLEN = 32


def _sim(inp: str):
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
    return words, out


def expected(inp: str) -> str:
    return "".join(line + "\r\n" for line in _sim(inp)[1])


def expected_disk(inp: str) -> dict:
    words, _ = _sim(inp)
    buf = bytearray()
    for w in words:
        rec = w.encode("latin-1", "replace")[:RECLEN - 1]
        buf += rec + b"\x00" * (RECLEN - len(rec))
    return {"DICT.TXT": bytes(buf)}


def gen(rng) -> str:
    cmds = []
    for _ in range(rng.randrange(1, 8)):
        r = rng.random()
        if r < 0.45:
            w = "".join(rng.choice("abcAB") for _ in range(rng.randrange(1, 5)))
            cmds.append(f"1 {w}")
        elif r < 0.85:
            p = "".join(rng.choice("abAB") for _ in range(rng.randrange(1, 3)))
            cmds.append(f"2 {p}")
        else:
            cmds.append("1 " + "x" * 31)
    cmds.append("3")
    return "\n".join(cmds) + "\n"
