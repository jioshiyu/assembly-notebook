"""9.1 参考模型：模拟"记事窗口"的可见文本（80x25，只比较屏幕文本）。

规则（与原版一致）：
- 从 (18,20) 开始打字；满 30 字符先换行；
- 回车换行但不写字符；
- 已在第 18 行再换行 → 窗口 rows 8..18 上卷一行（内容随之上移）；
- 0x1B（ESC）结束。
"""

W_TOP, W_BOT, W_LEFT, W_RIGHT = 8, 18, 20, 50
WRAP = 30


def _newline(grid, row):
    if row >= W_BOT:
        for r in range(W_TOP, W_BOT):
            grid[r][W_LEFT:W_RIGHT + 1] = grid[r + 1][W_LEFT:W_RIGHT + 1]
        grid[W_BOT][W_LEFT:W_RIGHT + 1] = [" "] * (W_RIGHT - W_LEFT + 1)
        return W_BOT
    return row + 1


def expected_screen(inp: str) -> str:
    grid = [[" "] * 80 for _ in range(25)]
    row, col, count = W_BOT, W_LEFT, 0
    for ch in inp:
        if ch == "\x1b":
            break
        if ch == "\r":
            row, col, count = _newline(grid, row), W_LEFT, 0
            continue
        if count >= WRAP:
            row, col, count = _newline(grid, row), W_LEFT, 0
        grid[row][col] = ch
        col += 1
        count += 1
    return "\n".join("".join(r).rstrip() for r in grid).rstrip()


def expected(inp: str) -> str:
    return ""          # 所有输出都走屏幕，没有 DOS stdout


def gen(rng) -> str:
    alphabet = "abcdefghij _0123456789"
    chars = []
    for _ in range(rng.randrange(1, 70)):
        chars.append("\r" if rng.random() < 0.08 else rng.choice(alphabet))
    return "".join(chars) + "\x1b"
