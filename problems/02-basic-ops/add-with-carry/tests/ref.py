"""1.1 参考模型：两个字节相加，输出 4 位十六进制和 + CRLF。

stdout 约定：所有程序输出以 CRLF（\\r\\n）结尾，与 DOS 行为一致。
"""


def expected(inp: str) -> str:
    a, b = (int(t, 16) for t in inp.split()[:2])
    return f"{(a + b) & 0xFFFF:04X}\r\n"


def gen(rng) -> str:
    return f"{rng.randrange(256):02X} {rng.randrange(256):02X}\n"
