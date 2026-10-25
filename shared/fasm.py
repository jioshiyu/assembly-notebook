"""fasm 编译封装（本机 fasm 随 emu8086 提供；找不到就报明确错误）。

沙箱约束：子进程不能用管道捕获输出（PermissionError），统一把 stdout/stderr
重定向到 build/ 下的日志文件，再读文件判断成败。
"""
from __future__ import annotations

import os
import subprocess
from pathlib import Path

CANDIDATES = [
    os.environ.get("FASM", ""),
    r"D:\emu8086\emu8086\fasm\FASM.EXE",
    r"C:\Program Files\fasm\FASM.EXE",
    "fasm",
]


def find_fasm() -> str:
    for c in CANDIDATES:
        if not c:
            continue
        if c == "fasm":
            try:
                subprocess.run(["fasm"], stdout=subprocess.DEVNULL,
                               stderr=subprocess.DEVNULL, timeout=10)
                return "fasm"
            except (OSError, subprocess.SubprocessError):
                continue
        if Path(c).exists():
            return c
    raise RuntimeError("找不到 fasm：设置环境变量 FASM 指向 FASM.EXE")


def assemble(src: Path, out: Path, log: Path | None = None):
    """编译 src -> out；返回 (ok, 日志文本)。"""
    fasm = find_fasm()
    out.parent.mkdir(parents=True, exist_ok=True)
    log = log or out.with_suffix(".log")
    with open(log, "w", encoding="utf-8", errors="replace") as fh:
        proc = subprocess.run([fasm, str(src), str(out)],
                              stdout=fh, stderr=subprocess.STDOUT,
                              cwd=str(src.parent), timeout=120)
    text = log.read_text(encoding="utf-8", errors="replace")
    ok = proc.returncode == 0 and out.exists()
    return ok, text
