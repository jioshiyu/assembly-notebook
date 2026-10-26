"""外部 oracle：用独立的 Unicorn Engine 跑同一份机器码，和自研模拟器对拍。

为什么需要它：自研模拟器 + 自研参考模型，两者同时错是"自洽的错误"，对拍抓不到。
Unicorn 是业界广泛使用的独立 CPU 模拟器（不是我们写的），同一份 .bin 在两边跑出
相同 stdout 与相同寄存器终态，才能说明"我们的解释器没跑偏"。

用法：
    python shared/oracle_unicorn.py                    # 全部题的第一条用例
    python shared/oracle_unicorn.py problems/02-basic-ops/add-with-carry
    python shared/oracle_unicorn.py --limit 5          # 只抽前 5 题

依赖 Unicorn（本沙箱 pip 装不了，用 tools/vendor_wheel.py unicorn 下 wheel 解压，
或 CI 里 pip install unicorn）。装不上时本脚本打印 SKIP 并退出 0，不阻塞本地开发。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "_vendor" / "site"))
import asm86  # noqa: E402

try:
    from unicorn import Uc, UC_ARCH_X86, UC_HOOK_INTR, UC_MODE_16
    from unicorn.x86_const import (
        UC_X86_REG_AH, UC_X86_REG_AL, UC_X86_REG_AX, UC_X86_REG_BX, UC_X86_REG_CX,
        UC_X86_REG_CS, UC_X86_REG_DI, UC_X86_REG_DL, UC_X86_REG_DS, UC_X86_REG_DX,
        UC_X86_REG_ES, UC_X86_REG_IP, UC_X86_REG_SI, UC_X86_REG_SP, UC_X86_REG_SS,
    )
    HAVE_UC = True
except ImportError:                                    # 本地没装就跳过
    HAVE_UC = False

SEG = 0x0700
ORG = 0x0100
BASE = SEG * 16 + ORG
MAX_INSTR = 5_000_000


class OracleError(Exception):
    pass


def run_unicorn(binary: bytes, stdin_text: str):
    """返回 (stdout, {寄存器})；只支持 INT 21h 的 08/02/09/4C。"""
    mu = Uc(UC_ARCH_X86, UC_MODE_16)
    mu.mem_map(0, 0x110000)
    mu.mem_write(BASE, binary)
    for reg, val in ((UC_X86_REG_CS, SEG), (UC_X86_REG_DS, SEG), (UC_X86_REG_ES, SEG),
                     (UC_X86_REG_SS, SEG), (UC_X86_REG_IP, ORG), (UC_X86_REG_SP, 0xFFFE),
                     (UC_X86_REG_AX, 0), (UC_X86_REG_BX, 0), (UC_X86_REG_CX, 0),
                     (UC_X86_REG_DX, 0)):
        mu.reg_write(reg, val)

    out: list[str] = []
    pending = list(stdin_text)

    def on_int(mu_, intno, user):
        if intno != 0x21:
            raise OracleError(f"未支持的 INT {intno:02X}h")
        ah = mu_.reg_read(UC_X86_REG_AH) & 0xFF
        if ah == 0x4C:
            mu_.emu_stop()
        elif ah == 0x08:
            if not pending:
                raise OracleError("input exhausted")
            mu_.reg_write(UC_X86_REG_AL, ord(pending.pop(0)))
        elif ah == 0x02:
            out.append(chr(mu_.reg_read(UC_X86_REG_DL) & 0xFF))
        elif ah == 0x09:
            ds = mu_.reg_read(UC_X86_REG_DS)
            dx = mu_.reg_read(UC_X86_REG_DX)
            addr = (ds * 16 + dx) & 0xFFFFF
            while True:
                c = mu_.mem_read(addr, 1)[0]
                if c == ord("$"):
                    break
                out.append(chr(c))
                addr += 1
        else:
            raise OracleError(f"未支持的 INT 21h AH={ah:02X}h")

    hook = mu.hook_add(UC_HOOK_INTR, on_int)
    mu.emu_start(BASE, 0, count=MAX_INSTR)
    mu.hook_del(hook)
    regs = {name: mu.reg_read(reg) for name, reg in (
        ("AX", UC_X86_REG_AX), ("BX", UC_X86_REG_BX), ("CX", UC_X86_REG_CX),
        ("DX", UC_X86_REG_DX), ("SI", UC_X86_REG_SI), ("DI", UC_X86_REG_DI))}
    return "".join(out), regs


def compare(prob: Path, case_idx=0) -> tuple[str, str]:
    """返回 (状态, 说明)：passed / failed / skipped。"""
    binp = ROOT / "build" / (prob.parent.name + "__" + prob.name + ".bin")
    if not binp.exists():
        return "skipped", "缺少 .bin（先跑 check.py 编译）"
    data = binp.read_bytes()
    cases = json.loads((prob / "tests" / "cases.json").read_text(encoding="utf-8"))
    inp = cases[case_idx].get("input", "")
    theirs = asm86.run_program(data, inp)
    if theirs["error"]:
        return "failed", f"自研模拟器出错：{theirs['error']}"
    try:
        ours_out, ours_regs = run_unicorn(data, inp)
    except OracleError as exc:
        if "未支持" in str(exc) or "exhausted" in str(exc):
            return "skipped", f"oracle 覆盖不到：{exc}"
        return "failed", f"oracle 崩溃：{exc}"
    problems = []
    if theirs["stdout"] != ours_out:
        problems.append(f"stdout 不一致：自研={theirs['stdout']!r} unicorn={ours_out!r}")
    for name, val in ours_regs.items():
        mine = theirs["regs"].get(name)
        if mine is None:
            continue
        if int(str(mine), 16) & 0xFFFF != val & 0xFFFF:
            problems.append(f"{name} 不一致：自研={mine} unicorn={val:#06x}")
    return ("passed", "") if not problems else ("failed", "；".join(problems))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--limit", type=int, default=0)
    ns = ap.parse_args(argv)
    if not HAVE_UC:
        print("SKIP: 没装 unicorn（本地：python tools/vendor_wheel.py unicorn；CI：pip install unicorn）")
        return 0
    probs = [Path(p).resolve() for p in ns.paths] or sorted(
        p.parent for p in (ROOT / "problems").glob("**/main.asm"))
    if ns.limit:
        probs = probs[: ns.limit]
    npass = nskip = bad = 0
    for prob in probs:
        status, why = compare(prob)
        name = prob.relative_to(ROOT / "problems")
        if status == "passed":
            npass += 1
            print(f"ORACLE PASS {name}")
        elif status == "skipped":
            nskip += 1
            print(f"ORACLE SKIP {name}: {why}")
        else:
            bad += 1
            print(f"ORACLE FAIL {name}: {why}")
    print(f"\n一致 {npass} / 跳过 {nskip} / 不一致 {bad}")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
