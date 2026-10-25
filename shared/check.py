"""质检三件套（汇编版）：编译 → 固定用例 → 随机对拍 → 统计。

用法：
    python shared/check.py                              # 跑全部题
    python shared/check.py problems/02-basic-ops/add-with-carry
    python shared/check.py --stress 50                  # 每题再对拍 50 组随机输入

每题目录约定：
    main.asm            我的实现（fasm 语法，org 100h，纯 stdin/stdout）
    original.asm        原始作业源码（照抄存档，MASM 语法，不参与编译）
    tests/ref.py        参考模型：expected(stdin_text) -> str；可选 gen(rng) -> str
    tests/cases.json    固定用例：[{"input": "...", "expect": "可选，写死做交叉校验"}]

证据标签：stdout 是**真实执行**模拟器得到的（measured）；字节数来自 fasm 产物
（measured）；周期数是估算（inferred），只用于同题横向对比。
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import asm86  # noqa: E402
import fasm  # noqa: E402

ROOT = HERE.parent
BUILD = ROOT / "build"


def load_ref(prob: Path):
    path = prob / "tests" / "ref.py"
    spec = importlib.util.spec_from_file_location(f"ref_{prob.name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def find_problems(paths) -> list[Path]:
    if paths:
        out = []
        for p in paths:
            p = Path(p).resolve()
            if (p / "main.asm").exists():
                out.append(p)
            else:
                out.extend(sorted(x.parent for x in p.glob("**/main.asm")))
        return out
    return sorted(x.parent for x in (ROOT / "problems").glob("**/main.asm"))


def run_one(prob: Path, stress: int, verbose: bool) -> dict:
    name = str(prob.relative_to(ROOT / "problems"))
    binp = BUILD / (prob.parent.name + "__" + prob.name + ".bin")
    ok, log = fasm.assemble(prob / "main.asm", binp)
    if not ok:
        return {"name": name, "ok": False, "why": "fasm 编译失败", "log": log[-800:]}
    data = binp.read_bytes()
    ref = load_ref(prob)
    cases = json.loads((prob / "tests" / "cases.json").read_text(encoding="utf-8"))
    fails: list[tuple[str, str]] = []
    icount = cycles = 0
    for case in cases:
        inp = case.get("input", "")
        res = asm86.run_program(data, inp)
        if res["error"]:
            fails.append((inp, f"运行错误：{res['error']}"))
            continue
        want = case.get("expect")
        if want is None:
            want = ref.expected(inp)
        if res["stdout"] != want:
            fails.append((inp, f"stdout={res['stdout']!r} 期望={want!r}"))
        want_screen = getattr(ref, "expected_screen", None)
        if want_screen is not None and res["screen"] != want_screen(inp):
            fails.append((inp, f"screen={res['screen']!r} 期望={want_screen(inp)!r}"))
        want_disk = getattr(ref, "expected_disk", None)
        if want_disk is not None:
            exp = want_disk(inp)
            if res["files"] != exp:
                fails.append((inp, f"文件系统不一致：{res['files']!r} 期望={exp!r}"))
        icount = max(icount, res["icount"])
        cycles = max(cycles, res["cycles"])
    stress_fail = 0
    if stress:
        rng = random.Random(20261025)
        gen = getattr(ref, "gen", None)
        if gen is None:
            fails.append(("", "stress 需要 ref.gen(rng)"))
        else:
            for _ in range(stress):
                inp = gen(rng)
                res = asm86.run_program(data, inp)
                if res["error"]:
                    fails.append((inp, f"运行错误：{res['error']}"))
                    stress_fail += 1
                    break
                if res["stdout"] != ref.expected(inp):
                    fails.append((inp, f"对拍不一致：{res['stdout']!r} vs {ref.expected(inp)!r}"))
                    stress_fail += 1
                    if stress_fail >= 3:
                        break
                icount = max(icount, res["icount"])
                cycles = max(cycles, res["cycles"])
    return {"name": name, "ok": not fails, "fails": fails, "bytes": len(data),
            "icount": icount, "cycles": cycles, "cases": len(cases)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--stress", type=int, default=0, help="每题随机对拍次数")
    ap.add_argument("--quiet", action="store_true")
    ns = ap.parse_args(argv)

    probs = find_problems(ns.paths)
    if not probs:
        print("没有找到任何 problems/*/*/main.asm")
        return 2
    BUILD.mkdir(parents=True, exist_ok=True)
    bad = 0
    for prob in probs:
        r = run_one(prob, ns.stress, not ns.quiet)
        if r["ok"]:
            print(f"PASS {r['name']:<44} bytes={r['bytes']:<4} 用例={r['cases']:<2} "
                  f"指令={r['icount']:<6} 周期≈{r['cycles']}")
        else:
            bad += 1
            print(f"FAIL {r['name']}")
            if r.get("log"):
                print(r["log"])
            for inp, why in r.get("fails", []):
                print(f"     input={inp!r} → {why}")
    print(f"\n{len(probs) - bad}/{len(probs)} passed")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
