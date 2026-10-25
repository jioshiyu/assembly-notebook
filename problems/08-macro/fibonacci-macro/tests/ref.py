"""10.3 参考模型：F(1)=F(2)=1 的斐波那契，按 16 位取模，十进制输出。"""


def fib(n: int) -> int:
    if n <= 2:
        return 1
    a, b = 1, 1
    for _ in range(n - 2):
        a, b = b, (a + b) & 0xFFFF
    return b


def expected(inp: str) -> str:
    toks = inp.split()
    n = int(toks[0], 16) if toks else 1
    return f"{fib(n)}\r\n"


def gen(rng) -> str:
    if rng.random() < 0.4:
        n = rng.choice([0, 1, 2, 3, 4, 5, 10, 24])
    else:
        n = rng.randrange(0, 30)
    return f"{n:04X}\n"
