"""8086 最小模拟器（课程作业子集）：跑 16 位 DOS 程序，抓 stdout 与屏幕。

设计目标：让"汇编作业也能对拍"——
  1) 装载 fasm 编译出的平坦二进制（org 100h）或 MZ 可执行文件；
  2) 逐条解释 8086 指令，不认识就报错（绝不静默猜）；
  3) 用 `check.py` 把程序输出与 Python 参考模型比对。

用法（手工调试）：
    python shared/asm86.py prog.bin --input "12" --regs

证据标签：指令语义按 Intel 8086 手册实现；周期数是**估算**（inferred），
只用于横向对比同一题的不同实现，不代表真实硬件时序。
"""
from __future__ import annotations

import sys

HALT_INPUT = "input exhausted"
MAX_INSTR_DEFAULT = 5_000_000


class Abort(Exception):
    pass


# 指令周期估算（inferred，8086 手册典型值）——只做同题横向对比
CYCLES = {
    "mov_rr": 2, "mov_rm": 9, "mov_mr": 9, "mov_ri": 4,
    "add": 3, "sub": 3, "cmp": 3, "and": 3, "or": 3, "xor": 3,
    "inc": 3, "dec": 3, "mul": 70, "imul": 80, "div": 80, "idiv": 100,
    "jmp": 15, "jcc": 16, "loop": 17, "call": 19, "ret": 16,
    "push": 15, "pop": 12, "int": 60, "lea": 2, "string": 18,
    "other": 4,
}

COND = {
    0x0: lambda f: f["OF"],
    0x1: lambda f: not f["OF"],
    0x2: lambda f: f["CF"],
    0x3: lambda f: not f["CF"],
    0x4: lambda f: f["ZF"],
    0x5: lambda f: not f["ZF"],
    0x6: lambda f: f["CF"] or f["ZF"],
    0x7: lambda f: not (f["CF"] or f["ZF"]),
    0x8: lambda f: f["SF"],
    0x9: lambda f: not f["SF"],
    0xA: lambda f: f["PF"],
    0xB: lambda f: not f["PF"],
    0xC: lambda f: bool(f["SF"]) != bool(f["OF"]),
    0xD: lambda f: bool(f["SF"]) == bool(f["OF"]),
    0xE: lambda f: f["ZF"] or (bool(f["SF"]) != bool(f["OF"])),
    0xF: lambda f: (not f["ZF"]) and (bool(f["SF"]) == bool(f["OF"])),
}

R8 = {"AL": ("AX", 0), "CL": ("CX", 0), "DL": ("DX", 0), "BL": ("BX", 0),
      "AH": ("AX", 8), "CH": ("CX", 8), "DH": ("DX", 8), "BH": ("BX", 8)}
R8I = ["AL", "CL", "DL", "BL", "AH", "CH", "DH", "BH"]
R16 = ["AX", "CX", "DX", "BX", "SP", "BP", "SI", "DI"]
SREG = ["ES", "CS", "SS", "DS"]


class Os:
    """DOS/BIOS 的最小子集：屏幕 80x25、键盘脚本、DOS 输出、**虚拟文件系统**。

    文件系统是内存里的字典（name -> bytearray）：测试完全封闭，不碰真磁盘；
    需要看落盘效果时用 `dump_files()`。
    """

    def __init__(self, stdin_text: str = ""):
        self.screen = [[" "] * 80 for _ in range(25)]
        self.attr = [[0x07] * 80 for _ in range(25)]
        self.cur = [0, 0]
        self.out: list[str] = []
        self.input = list(stdin_text)
        self.in_ptr = 0
        self.exit_code = None
        self.int_calls: list[str] = []
        self.files: dict[str, bytearray] = {}
        self.handles: dict[int, dict] = {}
        self.next_handle = 5

    # ---- 键盘 ----
    def next_key(self):
        if self.in_ptr >= len(self.input):
            raise Abort(HALT_INPUT)
        ch = self.input[self.in_ptr]
        self.in_ptr += 1
        return ch

    def peek_key(self):
        if self.in_ptr >= len(self.input):
            return None
        return self.input[self.in_ptr]

    # ---- 文件系统 ----
    def open_handle(self, name: str, mode: int) -> int:
        h = self.next_handle
        self.next_handle += 1
        self.handles[h] = {"name": name, "mode": mode, "pos": 0}
        return h

    def dump_files(self) -> dict[str, bytes]:
        return {k: bytes(v) for k, v in self.files.items()}

    # ---- 屏幕 ----
    def put(self, ch, color=None):
        c = self.cur[1]
        r = self.cur[0]
        if ch == "\r":
            c = 0
        elif ch == "\n":
            r += 1
            if r > 24:
                self.scroll(1, 0, 0, 24, 79)
                r = 24
        elif ch == "\b":
            c = max(0, c - 1)
        else:
            if 0 <= r < 25 and 0 <= c < 80:
                self.screen[r][c] = ch
                if color is not None:
                    self.attr[r][c] = color
            c += 1
            if c > 79:
                c = 0
                r += 1
                if r > 24:
                    self.scroll(1, 0, 0, 24, 79)
                    r = 24
        self.cur = [max(0, min(24, r)), max(0, min(79, c))]

    def scroll(self, lines, top, left, bot, right, attr=0x07):
        lines = min(lines, bot - top + 1) if lines else bot - top + 1
        for _ in range(lines):
            for r in range(top, bot):
                self.screen[r][left:right + 1] = self.screen[r + 1][left:right + 1]
                self.attr[r][left:right + 1] = self.attr[r + 1][left:right + 1]
            self.screen[bot][left:right + 1] = [" "] * (right - left + 1)
            self.attr[bot][left:right + 1] = [attr] * (right - left + 1)

    def clear(self):
        self.screen = [[" "] * 80 for _ in range(25)]
        self.attr = [[0x07] * 80 for _ in range(25)]
        self.cur = [0, 0]

    def text(self) -> str:
        return "".join(self.out)

    def screen_text(self) -> str:
        return "\n".join("".join(row).rstrip() for row in self.screen).rstrip()


class CPU:
    def __init__(self, os_: Os | None = None, max_instr: int = MAX_INSTR_DEFAULT):
        self.mem = bytearray(0x100000)
        self.r_ = {k: 0 for k in R16}
        self.sreg = {"CS": 0, "DS": 0, "ES": 0, "SS": 0}
        self.f = {"CF": 0, "ZF": 0, "SF": 0, "OF": 0, "AF": 0, "PF": 0, "DF": 0, "IF": 1}
        self.ip = 0x100
        self.os = os_ or Os()
        self.max_instr = max_instr
        self.icount = 0
        self.cycles = 0
        self.seg_override = None
        self.rep = None
        self.halted = False
        self.trace: list[str] | None = None

    # ================= 基础访问 =================
    def phys(self, seg, off):
        return ((seg << 4) + (off & 0xFFFF)) & 0xFFFFF

    def r(self, name):
        return self.r_[name]

    def setr(self, name, val):
        self.r_[name] = val & 0xFFFF

    def get8(self, name):
        base, sh = R8[name]
        return (self.r_[base] >> sh) & 0xFF

    def set8(self, name, val):
        base, sh = R8[name]
        v = self.r_[base]
        v = (v & ~(0xFF << sh)) | ((val & 0xFF) << sh)
        self.r_[base] = v & 0xFFFF

    def rd8(self, addr):
        return self.mem[addr & 0xFFFFF]

    def wr8(self, addr, val):
        self.mem[addr & 0xFFFFF] = val & 0xFF

    def rd16(self, addr):
        a = addr & 0xFFFFF
        return self.mem[a] | (self.mem[(a + 1) & 0xFFFFF] << 8)

    def wr16(self, addr, val):
        a = addr & 0xFFFFF
        self.mem[a] = val & 0xFF
        self.mem[(a + 1) & 0xFFFFF] = (val >> 8) & 0xFF

    def stack_push(self, val):
        self.setr("SP", self.r_["SP"] - 2)
        self.wr16(self.phys(self.sreg["SS"], self.r_["SP"]), val)

    def stack_pop(self):
        v = self.rd16(self.phys(self.sreg["SS"], self.r_["SP"]))
        self.setr("SP", self.r_["SP"] + 2)
        return v

    # ================= 取指/取操作数 =================
    def fetch8(self):
        a = self.phys(self.sreg["CS"], self.ip)
        self.ip = (self.ip + 1) & 0xFFFF
        return self.mem[a]

    def fetch16(self):
        lo = self.fetch8()
        hi = self.fetch8()
        return lo | (hi << 8)

    def fetch_s8(self):
        v = self.fetch8()
        return v - 0x100 if v & 0x80 else v

    def fetch_s16(self):
        v = self.fetch16()
        return v - 0x10000 if v & 0x8000 else v

    def _ea(self, mod, rm):
        seg = self.sreg["DS"]
        if rm == 0:
            base = self.r_["BX"] + self.r_["SI"]
        elif rm == 1:
            base = self.r_["BX"] + self.r_["DI"]
        elif rm == 2:
            base = self.r_["BP"] + self.r_["SI"]
            seg = self.sreg["SS"]
        elif rm == 3:
            base = self.r_["BP"] + self.r_["DI"]
            seg = self.sreg["SS"]
        elif rm == 4:
            base = self.r_["SI"]
        elif rm == 5:
            base = self.r_["DI"]
        elif rm == 6:
            if mod == 0:
                off = self.fetch16()
                return self.phys(self.sreg["DS"], off)
            base = self.r_["BP"]
            seg = self.sreg["SS"]
        else:
            base = self.r_["BX"]
        if mod == 1:
            base += self.fetch_s8()
        elif mod == 2:
            base = (base + self.fetch16()) & 0xFFFF
        if self.seg_override:
            seg = self.sreg[self.seg_override]
        self._last_off = base & 0xFFFF
        return self.phys(seg, base & 0xFFFF)

    def modrm(self):
        """返回 (mod, reg, rm, addr_or_None)。"""
        m = self.fetch8()
        mod, reg, rm = m >> 6, (m >> 3) & 7, m & 7
        addr = None if mod == 3 else self._ea(mod, rm)
        return mod, reg, rm, addr

    # ================= 标志与 ALU =================
    def szp(self, val, size):
        bits = size * 8
        mask = (1 << bits) - 1
        v = val & mask
        self.f["ZF"] = 1 if v == 0 else 0
        self.f["SF"] = (v >> (bits - 1)) & 1
        self.f["PF"] = 1 if bin(v & 0xFF).count("1") % 2 == 0 else 0
        return v

    def add(self, a, b, size, carry=0):
        bits = size * 8
        mask = (1 << bits) - 1
        r = a + b + carry
        res = r & mask
        self.f["CF"] = 1 if r > mask else 0
        sa, sb, sr = (a >> (bits - 1)) & 1, (b >> (bits - 1)) & 1, (res >> (bits - 1)) & 1
        self.f["OF"] = 1 if sa == sb and sr != sa else 0
        self.f["AF"] = 1 if ((a & 0xF) + (b & 0xF) + carry) > 0xF else 0
        return self.szp(res, size)

    def sub_(self, a, b, size, borrow=0):
        bits = size * 8
        mask = (1 << bits) - 1
        r = a - b - borrow
        res = r & mask
        self.f["CF"] = 1 if r < 0 else 0
        sa, sb, sr = (a >> (bits - 1)) & 1, (b >> (bits - 1)) & 1, (res >> (bits - 1)) & 1
        self.f["OF"] = 1 if sa != sb and sr != sa else 0
        self.f["AF"] = 1 if ((a & 0xF) - (b & 0xF) - borrow) < 0 else 0
        return self.szp(res, size)

    def logic(self, val, size):
        self.f["CF"] = 0
        self.f["OF"] = 0
        return self.szp(val, size)

    def alu(self, op, a, b, size):
        if op == 0:
            return self.add(a, b, size)
        if op == 1:
            return self.logic(a | b, size)
        if op == 2:
            return self.add(a, b, size, self.f["CF"])
        if op == 3:
            return self.sub_(a, b, size, self.f["CF"])
        if op == 4:
            return self.logic(a & b, size)
        if op == 5:
            return self.sub_(a, b, size)
        if op == 6:
            return self.logic(a ^ b, size)
        if op == 7:
            self.sub_(a, b, size)
            return a
        raise Abort(f"unknown ALU op {op}")

    # ================= 中断 =================
    def call_int(self, vec):
        self.os.int_calls.append(f"{vec:02X}")
        if vec == 0x21:
            self._int21()
        elif vec == 0x10:
            self._int10()
        elif vec == 0x16:
            self._int16()
        elif vec == 0x20:
            raise _Exit(0)
        else:
            raise Abort(f"INT {vec:02X}h 未实现（程序用到了超出子集的中断）")

    def _int21(self):
        ah = self.get8("AH")
        os_ = self.os
        if ah == 0x01:
            ch = os_.next_key()
            os_.out.append(ch)
            os_.put(ch)
            self.set8("AL", ord(ch))
        elif ah == 0x02:
            ch = chr(self.get8("DL"))
            os_.out.append(ch)
            os_.put(ch)
        elif ah == 0x06:
            ch = os_.next_key() if os_.in_ptr < len(os_.input) else "\x00"
            self.set8("AL", ord(ch))
            os_.put(ch)
            os_.out.append(ch)
        elif ah == 0x07:
            self.set8("AL", ord(os_.next_key()))
        elif ah == 0x08:
            self.set8("AL", ord(os_.next_key()))
        elif ah == 0x09:
            addr = self.phys(self.sreg["DS"], self.r_["DX"])
            chars = []
            for i in range(0, 4096):
                c = self.mem[(addr + i) & 0xFFFFF]
                if c == 0x24:
                    break
                chars.append(chr(c))
            s = "".join(chars)
            os_.out.append(s)
            for ch in s:
                os_.put(ch)
        elif ah == 0x0A:
            # 缓冲输入：buf[0]=max, buf[1]=实际长度, buf[2:]=内容
            addr = self.phys(self.sreg["DS"], self.r_["DX"])
            limit = self.mem[addr]
            chars = []
            while len(chars) < max(0, limit - 1):
                ch = os_.next_key()
                if ch in "\r\n":
                    os_.put("\r")
                    os_.put("\n")
                    os_.out.append("\n")
                    break
                if ch == "\b":
                    if chars:
                        chars.pop()
                        os_.put("\b")
                    continue
                chars.append(ch)
                os_.out.append(ch)
                os_.put(ch)
            self.mem[addr + 1] = len(chars)
            for i, ch in enumerate(chars):
                self.mem[addr + 2 + i] = ord(ch)
        elif ah == 0x4C:
            raise _Exit(self.get8("AL"))
        elif ah in (0x3C, 0x3D, 0x3E, 0x3F, 0x40, 0x41, 0x42):
            self._dos_file(ah)
        elif ah == 0x2A:
            self.setr("CX", 2026)
            self.set8("DH", 10)
            self.set8("DL", 25)
            self.set8("AL", 0)
        else:
            raise Abort(f"INT 21h AH={ah:02X}h 未实现")

    def _read_asciiz(self, seg, off, limit=128) -> str:
        addr = self.phys(seg, off)
        out = []
        for i in range(limit):
            c = self.mem[(addr + i) & 0xFFFFF]
            if c == 0:
                break
            out.append(chr(c))
        return "".join(out)

    def _dos_fail(self, code):
        self.f["CF"] = 1
        self.setr("AX", code)

    def _dos_file(self, ah):
        """INT 21h 文件子集：3C 创建 / 3D 打开 / 3E 关闭 / 3F 读 / 40 写 / 41 删除 / 42 定位。

        文件存在内存里（`Os.files`），句柄从 5 开始——和真 DOS 一样，0–4 是标准设备。
        """
        os_ = self.os
        ds = self.sreg["DS"]
        if ah == 0x3C:                      # 创建（已存在则截断）
            name = self._read_asciiz(ds, self.r_["DX"])
            os_.files[name] = bytearray()
            self.setr("AX", os_.open_handle(name, 1))
            self.f["CF"] = 0
        elif ah == 0x3D:                    # 打开
            name = self._read_asciiz(ds, self.r_["DX"])
            if name not in os_.files:
                return self._dos_fail(2)    # 文件未找到
            self.setr("AX", os_.open_handle(name, self.get8("AL")))
            self.f["CF"] = 0
        elif ah == 0x3E:                    # 关闭
            os_.handles.pop(self.r_["BX"], None)
            self.f["CF"] = 0
        elif ah == 0x3F:                    # 读
            h = os_.handles.get(self.r_["BX"])
            if not h:
                return self._dos_fail(6)
            buf = os_.files[h["name"]]
            n = max(0, min(self.r_["CX"], len(buf) - h["pos"]))
            addr = self.phys(ds, self.r_["DX"])
            for i in range(n):
                self.mem[(addr + i) & 0xFFFFF] = buf[h["pos"] + i]
            h["pos"] += n
            self.setr("AX", n)
            self.f["CF"] = 0
        elif ah == 0x40:                    # 写
            h = os_.handles.get(self.r_["BX"])
            if not h:
                return self._dos_fail(6)
            buf = os_.files[h["name"]]
            addr = self.phys(ds, self.r_["DX"])
            n = self.r_["CX"]
            data = bytes(self.mem[(addr + i) & 0xFFFFF] for i in range(n))
            pos = h["pos"]
            if pos > len(buf):
                buf.extend(b"\x00" * (pos - len(buf)))
            buf[pos:pos + n] = data
            h["pos"] += n
            self.setr("AX", n)
            self.f["CF"] = 0
        elif ah == 0x41:                    # 删除
            name = self._read_asciiz(ds, self.r_["DX"])
            if name not in os_.files:
                return self._dos_fail(2)
            del os_.files[name]
            self.f["CF"] = 0
        elif ah == 0x42:                    # 定位（AL=0 头/1 当前/2 尾）
            h = os_.handles.get(self.r_["BX"])
            if not h:
                return self._dos_fail(6)
            off = (self.r_["CX"] << 16) | self.r_["DX"]
            if off & 0x80000000:
                off -= 0x100000000
            origin = self.get8("AL")
            base = 0 if origin == 0 else h["pos"] if origin == 1 else len(os_.files[h["name"]])
            newpos = max(0, base + off)
            h["pos"] = newpos
            self.setr("AX", newpos & 0xFFFF)
            self.setr("DX", (newpos >> 16) & 0xFFFF)
            self.f["CF"] = 0

    def _int10(self):
        ah = self.get8("AH")
        al = self.get8("AL")
        os_ = self.os
        if ah == 0x00:
            os_.clear()
        elif ah in (0x01, 0x02, 0x03, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0E, 0x0F, 0x13):
            if ah in (0x06, 0x07):
                top = self.get8("CH")
                left = self.get8("CL")
                bot = self.get8("DH")
                right = self.get8("DL")
                lines = al if al else (bot - top + 1)
                if ah == 0x06:
                    os_.scroll(lines, min(top, bot), min(left, right),
                               max(top, bot), max(left, right), self.get8("BH"))
                else:
                    for _ in range(lines if al else bot - top + 1):
                        for r in range(max(top, bot), min(top, bot) - 1, -1):
                            if r - 1 >= min(top, bot):
                                os_.screen[r][min(left, right):max(left, right) + 1] = \
                                    os_.screen[r - 1][min(left, right):max(left, right) + 1]
                        os_.screen[min(top, bot)][min(left, right):max(left, right) + 1] = \
                            [" "] * (max(left, right) - min(left, right) + 1)
            elif ah == 0x02:
                os_.cur = [self.get8("DH"), self.get8("DL")]
            elif ah == 0x03:
                self.set8("DH", os_.cur[0])
                self.set8("DL", os_.cur[1])
            elif ah == 0x08:
                r, c = os_.cur
                self.set8("AL", ord(os_.screen[r][c]) if os_.screen[r][c] != " " else 0x20)
                self.set8("AH", os_.attr[r][c])
            elif ah == 0x09:
                r, c = os_.cur
                for i in range(al if al else 1):
                    if c + i < 80:
                        os_.screen[r][c + i] = chr(self.get8("DL"))
                        os_.attr[r][c + i] = self.get8("BL")
            elif ah == 0x0A:
                r, c = os_.cur
                for i in range(al if al else 1):
                    if c + i < 80:
                        os_.screen[r][c + i] = chr(self.get8("DL"))
            elif ah == 0x0E:
                os_.put(chr(al))
            elif ah == 0x0F:
                self.set8("AL", 3)
                self.set8("AH", 80)
        elif ah == 0x0D:
            pass
        else:
            raise Abort(f"INT 10h AH={ah:02X}h 未实现")

    def _int16(self):
        ah = self.get8("AH")
        os_ = self.os
        if ah == 0x00:
            ch = os_.next_key()
            self.setr("AX", ord(ch))
        elif ah == 0x01:
            nxt = os_.peek_key()
            self.f["ZF"] = 0 if nxt else 1
            if nxt:
                self.setr("AX", ord(nxt))
        else:
            raise Abort(f"INT 16h AH={ah:02X}h 未实现")

    # ================= 主循环 =================
    def run(self):
        steps = 0
        while not self.halted:
            if steps >= self.max_instr:
                raise Abort(f"执行超过 {self.max_instr} 条指令，疑似死循环")
            steps += 1
            self.step()

    def step(self):
        self.seg_override = None
        self.rep = None
        while True:
            b = self.fetch8()
            if b in (0x26, 0x2E, 0x36, 0x3E):
                self.seg_override = {0x26: "ES", 0x2E: "CS", 0x36: "SS", 0x3E: "DS"}[b]
            elif b in (0xF2, 0xF3):
                self.rep = "ne" if b == 0xF2 else "re"
            else:
                op = b
                break
        self.icount += 1
        self._exec(op)
        return op

    # --- 指令实现 ---
    def _exec(self, op):
        self.cycles += CYCLES.get("other", 4)
        if self.rep in ("re", "ne") and op not in (0xA4, 0xA5, 0xA6, 0xA7, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF):
            raise Abort(f"REP 前缀用在 0x{op:02X} 上，未实现")
        # mov
        if op in (0x88, 0x89, 0x8A, 0x8B):
            size = 1 if op in (0x88, 0x8A) else 2
            mod, reg, rm, addr = self.modrm()
            if op in (0x88, 0x89):
                src = self._getreg(reg, size)
                self._put(mod, rm, addr, size, src)
            else:
                v = self._get(mod, rm, addr, size)
                self._setreg(reg, size, v)
        elif op in (0x8C, 0x8E):
            mod, reg, rm, addr = self.modrm()
            if op == 0x8E:
                self.sreg[SREG[reg]] = self._get(mod, rm, addr, 2)
            else:
                self._put(mod, rm, addr, 2, self.sreg[SREG[reg]])
        elif 0xB0 <= op <= 0xBF:
            reg = op & 7
            if op < 0xB8:
                self.set8(R8I[reg], self.fetch8())
            else:
                self.setr(R16[reg], self.fetch16())
        elif op in (0xA0, 0xA1, 0xA2, 0xA3):
            size = 1 if op in (0xA0, 0xA2) else 2
            off = self.fetch16()
            addr = self.phys(self.sreg["DS"], off)
            if op in (0xA0, 0xA1):
                self._setreg(0, size, self._rd(addr, size))
            else:
                self._wr(addr, size, self._getreg(0, size))
        elif op in (0xC6, 0xC7):
            size = 1 if op == 0xC6 else 2
            mod, reg, rm, addr = self.modrm()
            imm = self.fetch8() if size == 1 else self.fetch16()
            self._put(mod, rm, addr, size, imm)
        elif op == 0x8D:  # lea：取有效地址偏移，不访存
            mod, reg, rm, addr = self.modrm()
            if mod == 3:
                raise Abort("LEA 的操作数不能是寄存器")
            self.setr(R16[reg], self._last_off)
        elif op in (0x86, 0x87):
            size = 1 if op == 0x86 else 2
            mod, reg, rm, addr = self.modrm()
            a = self._getreg(reg, size)
            b = self._get(mod, rm, addr, size)
            self._setreg(reg, size, b)
            self._put(mod, rm, addr, size, a)
            self.cycles += CYCLES["mov_rr"]
        elif 0x90 <= op <= 0x97:
            if op != 0x90:
                reg = op & 7
                a = self.r_["AX"]
                self.setr("AX", self.r_[R16[reg]])
                self.setr(R16[reg], a)
        elif 0x40 <= op <= 0x4F:
            reg = R16[op & 7]
            if op < 0x48:
                v = self.add(self.r(reg), 1, 2)
            else:
                v = self.sub_(self.r(reg), 1, 2)
            self.setr(reg, v)
        elif op in (0x6A, 0x68):  # PUSH imm8 / imm16（80186+，fasm 常这么编）
            imm = self.fetch_s8() & 0xFFFF if op == 0x6A else self.fetch16()
            self.stack_push(imm)
        elif 0x50 <= op <= 0x57:
            self.stack_push(self.r_[R16[op & 7]])
        elif 0x58 <= op <= 0x5F:
            self.setr(R16[op & 7], self.stack_pop())
        elif op in (0x06, 0x0E, 0x16, 0x1E):
            self.stack_push(self.sreg[SREG[(op >> 3) & 3]])
        elif op in (0x07, 0x17, 0x1F):
            self.sreg[SREG[(op >> 3) & 3]] = self.stack_pop()
        elif op == 0x9C:
            self.stack_push(self._flags_word())
        elif op == 0x9D:
            self._set_flags_word(self.stack_pop())
        elif op in (0x00, 0x01, 0x08, 0x09, 0x10, 0x11, 0x18, 0x19,
                    0x20, 0x21, 0x28, 0x29, 0x30, 0x31, 0x38, 0x39):
            # r/m <- r/m op reg
            size = 1 if op & 1 == 0 else 2
            mod, reg, rm, addr = self.modrm()
            dst = self._get(mod, rm, addr, size)
            src = self._getreg(reg, size)
            res = self.alu(op >> 3, dst, src, size)
            if (op >> 3) != 7:
                self._put(mod, rm, addr, size, res)
        elif op in (0x02, 0x03, 0x0A, 0x0B, 0x12, 0x13, 0x1A, 0x1B,
                    0x22, 0x23, 0x2A, 0x2B, 0x32, 0x33, 0x3A, 0x3B):
            # reg <- reg op r/m
            size = 1 if op & 1 == 0 else 2
            mod, reg, rm, addr = self.modrm()
            src = self._get(mod, rm, addr, size)
            dst = self._getreg(reg, size)
            res = self.alu(op >> 3, dst, src, size)
            if (op >> 3) != 7:
                self._setreg(reg, size, res)
        elif op in (0x04, 0x05, 0x0C, 0x0D, 0x14, 0x15, 0x1C, 0x1D,
                    0x24, 0x25, 0x2C, 0x2D, 0x34, 0x35, 0x3C, 0x3D):
            size = 1 if op & 1 == 0 else 2
            imm = self.fetch8() if size == 1 else self.fetch16()
            a = self._getreg(0, size)
            res = self.alu(op >> 3, a, imm, size)
            if (op >> 3) != 7:
                self._setreg(0, size, res)
        elif op in (0x80, 0x81, 0x83):
            size = 1 if op == 0x80 else 2
            mod, reg, rm, addr = self.modrm()
            if op == 0x83:
                imm = self.fetch_s8() & 0xFFFF
            else:
                imm = self.fetch8() if size == 1 else self.fetch16()
            a = self._get(mod, rm, addr, size)
            res = self.alu(reg, a, imm, size)
            if reg != 7:
                self._put(mod, rm, addr, size, res)
        elif op in (0x84, 0x85):
            size = 1 if op == 0x84 else 2
            mod, reg, rm, addr = self.modrm()
            self.logic(self._get(mod, rm, addr, size) & self._getreg(reg, size), size)
        elif op in (0xF6, 0xF7):
            size = 1 if op == 0xF6 else 2
            mod, reg, rm, addr = self.modrm()
            if reg == 0 or reg == 1:
                imm = self.fetch8() if size == 1 else self.fetch16()
                self.logic(self._get(mod, rm, addr, size) & imm, size)
            elif reg == 2:
                self._put(mod, rm, addr, size, ~self._get(mod, rm, addr, size))
            elif reg == 3:
                v = self._get(mod, rm, addr, size)
                self._put(mod, rm, addr, size, self.sub_(0, v, size))
            elif reg in (4, 5):
                src = self._get(mod, rm, addr, size)
                self.cycles += CYCLES["mul" if reg == 4 else "imul"]
                if reg == 5:  # IMUL：符号扩展乘法
                    if size == 1:
                        sa = self.get8("AL")
                        sa = sa - 0x100 if sa & 0x80 else sa
                        sb = src - 0x100 if src & 0x80 else src
                        res = sa * sb
                        self.setr("AX", res & 0xFFFF)
                        self.f["CF"] = self.f["OF"] = 1 if not -0x80 <= res <= 0x7F else 0
                    else:
                        sa = self.r_["AX"]
                        sa = sa - 0x10000 if sa & 0x8000 else sa
                        sb = src - 0x10000 if src & 0x8000 else src
                        res = sa * sb
                        self.setr("AX", res & 0xFFFF)
                        self.setr("DX", (res >> 16) & 0xFFFF)
                        self.f["CF"] = self.f["OF"] = 1 if not -0x8000 <= res <= 0x7FFF else 0
                elif size == 1:
                    res = self.get8("AL") * src
                    self.setr("AX", res & 0xFFFF)
                    self.f["CF"] = self.f["OF"] = 1 if res > 0xFF else 0
                else:
                    res = self.r_["AX"] * src
                    self.setr("AX", res & 0xFFFF)
                    self.setr("DX", (res >> 16) & 0xFFFF)
                    self.f["CF"] = self.f["OF"] = 1 if res > 0xFFFF else 0
            elif reg in (6, 7):
                src = self._get(mod, rm, addr, size)
                self.cycles += CYCLES["div"]
                if reg == 7:  # IDIV：有符号除法，商向零截断
                    top = 0x80 if size == 1 else 0x8000
                    sb = src - (top * 2) if src & top else src
                    if sb == 0:
                        raise Abort("除零（IDIV 的除数为 0）")
                    if size == 1:
                        sa = self.r_["AX"]
                        sa = sa - 0x10000 if sa & 0x8000 else sa
                    else:
                        sa = (self.r_["DX"] << 16) | self.r_["AX"]
                        sa = sa - 0x100000000 if sa & 0x80000000 else sa
                    q = abs(sa) // abs(sb)
                    q = q if (sa >= 0) == (sb >= 0) else -q
                    r = sa - q * sb
                    if size == 1:
                        if not -0x80 <= q <= 0x7F:
                            raise Abort("IDIV 8 位商溢出")
                        self.set8("AL", q & 0xFF)
                        self.set8("AH", r & 0xFF)
                    else:
                        if not -0x8000 <= q <= 0x7FFF:
                            raise Abort("IDIV 16 位商溢出")
                        self.setr("AX", q & 0xFFFF)
                        self.setr("DX", r & 0xFFFF)
                elif size == 1:
                    if src == 0:
                        raise Abort("除零（DIV 的除数为 0）")
                    ax = self.r_["AX"]
                    q, r = divmod(ax, src)
                    if q > 0xFF:
                        raise Abort("DIV 8 位商溢出（quotient > 255）")
                    self.set8("AL", q)
                    self.set8("AH", r)
                else:
                    if src == 0:
                        raise Abort("除零（DIV 的除数为 0）")
                    dx, ax = self.r_["DX"], self.r_["AX"]
                    num = (dx << 16) | ax
                    q, r = divmod(num, src)
                    if q > 0xFFFF:
                        raise Abort("DIV 16 位商溢出")
                    self.setr("AX", q)
                    self.setr("DX", r)
        elif op in (0xFE, 0xFF):
            size = 1 if op == 0xFE else 2
            mod, reg, rm, addr = self.modrm()
            if reg == 0:
                self._put(mod, rm, addr, size, self.add(self._get(mod, rm, addr, size), 1, size))
            elif reg == 1:
                self._put(mod, rm, addr, size, self.sub_(self._get(mod, rm, addr, size), 1, size))
            elif reg == 2:
                target = self._get(mod, rm, addr, 2)
                self.stack_push(self.ip)
                self.ip = target & 0xFFFF
            elif reg == 4:
                self.ip = self._get(mod, rm, addr, 2) & 0xFFFF
            elif reg == 6:
                self.stack_push(self._get(mod, rm, addr, 2))
            else:
                raise Abort(f"FF /{reg} 未实现")
        elif op in (0xC0, 0xC1, 0xD0, 0xD1, 0xD2, 0xD3):
            size = 1 if op in (0xC0, 0xD0, 0xD2) else 2
            mod, reg, rm, addr = self.modrm()
            if op in (0xC0, 0xC1):   # 80186+ 立即数移位（emu8086 接受）
                cnt = self.fetch8() & 0x1F
            elif op in (0xD0, 0xD1):
                cnt = 1
            else:
                cnt = self.get8("CL") & 0x1F
            v = self._get(mod, rm, addr, size)
            v = self._shift(reg, v, cnt, size)
            self.szp(v, size)
            self._put(mod, rm, addr, size, v)
        elif op == 0xD7:  # XLAT/XLATB：AL = [BX+AL]
            seg = self.sreg[self.seg_override] if self.seg_override else self.sreg["DS"]
            self.set8("AL", self.mem[self.phys(seg, (self.r_["BX"] + self.get8("AL")) & 0xFFFF)])
        elif op == 0x98:  # cbw
            al = self.get8("AL")
            self.setr("AX", al - 0x100 if al & 0x80 else al)
        elif op == 0x99:  # cwd
            self.setr("DX", 0xFFFF if self.r_["AX"] & 0x8000 else 0)
        elif op in (0xA4, 0xA5, 0xA6, 0xA7, 0xAA, 0xAB, 0xAC, 0xAD, 0xAE, 0xAF):
            self._string(op)
        elif op == 0x0F:  # 80186+ 的两个字节指令：Jcc rel16 与 SETcc r/m8
            sub = self.fetch8()
            if 0x80 <= sub <= 0x8F:
                rel = self.fetch_s16()
                if COND[sub & 0xF](self.f):
                    self.ip = (self.ip + rel) & 0xFFFF
            elif 0x90 <= sub <= 0x9F:
                mod, _reg, rm, addr = self.modrm()
                self._put(mod, rm, addr, 1, 1 if COND[sub & 0xF](self.f) else 0)
            else:
                raise Abort(f"未实现的 0F {sub:02X} 指令（80186+ 扩展）")
        elif 0x70 <= op <= 0x7F:
            rel = self.fetch_s8()
            if COND[op & 0xF](self.f):
                self.ip = (self.ip + rel) & 0xFFFF
        elif op == 0xE9:
            rel = self.fetch_s16()          # 必须先取完操作数，ip 才指向下一条
            self.ip = (self.ip + rel) & 0xFFFF
        elif op == 0xEB:
            rel = self.fetch_s8()
            self.ip = (self.ip + rel) & 0xFFFF
        elif op == 0xE8:
            rel = self.fetch_s16()
            self.stack_push(self.ip)
            self.ip = (self.ip + rel) & 0xFFFF
        elif op == 0x9A:  # far call
            off = self.fetch16()
            seg = self.fetch16()
            self.stack_push(self.sreg["CS"])
            self.stack_push(self.ip)
            self.sreg["CS"] = seg
            self.ip = off
        elif op == 0xEA:  # far jmp
            off = self.fetch16()
            seg = self.fetch16()
            self.sreg["CS"] = seg
            self.ip = off
        elif 0xE0 <= op <= 0xE3:
            rel = self.fetch_s8()
            if op == 0xE3:  # JCXZ 不改 CX
                cx = self.r_["CX"]
            else:
                cx = (self.r_["CX"] - 1) & 0xFFFF
                self.setr("CX", cx)
            take = False
            if op == 0xE0:
                take = cx != 0 and not self.f["ZF"]
            elif op == 0xE1:
                take = cx != 0 and self.f["ZF"]
            elif op == 0xE2:
                take = cx != 0
            else:
                take = cx == 0
            if take:
                self.ip = (self.ip + rel) & 0xFFFF
        elif op in (0xC3, 0xC2):
            if op == 0xC2:
                self.fetch16()
            self.ip = self.stack_pop() & 0xFFFF
        elif op == 0xCB or op == 0xCA:
            if op == 0xCA:
                self.fetch16()
            self.ip = self.stack_pop() & 0xFFFF
            self.sreg["CS"] = self.stack_pop()
        elif op == 0xCD:
            self.cycles += CYCLES["int"]
            self.call_int(self.fetch8())
        elif op == 0xCC:
            raise Abort("INT3 断点")
        elif op == 0xF4:
            self.halted = True
        elif op == 0x9E:
            pass
        elif op == 0xF8:
            self.f["CF"] = 0
        elif op == 0xF9:
            self.f["CF"] = 1
        elif op == 0xFA:
            self.f["IF"] = 0
        elif op == 0xFB:
            self.f["IF"] = 1
        elif op == 0xFC:
            self.f["DF"] = 0
        elif op == 0xFD:
            self.f["DF"] = 1
        elif op == 0xF5:
            self.f["CF"] ^= 1
        elif op == 0xD4:  # aam
            base = self.fetch8() or 10
            al = self.get8("AL")
            self.set8("AH", al // base)
            self.set8("AL", al % base)
            self.szp(self.get8("AL"), 1)
        elif op == 0xD5:  # aad
            base = self.fetch8() or 10
            al = (self.get8("AH") * base + self.get8("AL")) & 0xFF
            self.set8("AL", al)
            self.set8("AH", 0)
            self.szp(al, 1)
        elif op == 0x27:  # daa
            al = self.get8("AL")
            if (al & 0xF) > 9 or self.f["AF"]:
                al = (al + 6) & 0xFF
                self.f["AF"] = 1
            else:
                self.f["AF"] = 0
            if al > 0x9F or self.f["CF"]:
                al = (al + 0x60) & 0xFF
                self.f["CF"] = 1
            else:
                self.f["CF"] = 0
            self.set8("AL", al)
            self.szp(al, 1)
        elif op in (0xE4, 0xE5, 0xE6, 0xE7):
            self.fetch8()  # 端口号忽略（课程作业不依赖真实外设）
        elif op == 0x2E or op == 0x26:
            pass
        elif op == 0x8F:
            mod, reg, rm, addr = self.modrm()
            self._put(mod, rm, addr, 2, self.stack_pop())
        elif op == 0x91:
            pass
        else:
            raise Abort(f"未实现的指令 0x{op:02X}（IP=0x{self.ip - 1:04X}）")

    def _getreg(self, reg, size):
        return self.get8(R8I[reg]) if size == 1 else self.r_[R16[reg]]

    def _setreg(self, reg, size, val):
        if size == 1:
            self.set8(R8I[reg], val)
        else:
            self.setr(R16[reg], val)

    def _get(self, mod, rm, addr, size):
        if mod == 3:
            return self._getreg(rm, size)
        return self._rd(addr, size)

    def _put(self, mod, rm, addr, size, val):
        if mod == 3:
            self._setreg(rm, size, val)
        else:
            self._wr(addr, size, val)

    def _rd(self, addr, size):
        return self.rd8(addr) if size == 1 else self.rd16(addr)

    def _shift(self, reg, v, cnt, size):
        """实现 8086 移位/循环移位（reg 是 group2 的 /digit）。"""
        bits = size * 8
        mask = (1 << bits) - 1
        v &= mask
        for _ in range(cnt):
            if reg == 0:  # rol
                c = (v >> (bits - 1)) & 1
                v = ((v << 1) | c) & mask
                self.f["CF"] = c
            elif reg == 1:  # ror
                c = v & 1
                v = ((v >> 1) | (c << (bits - 1))) & mask
                self.f["CF"] = c
            elif reg == 2:  # rcl
                c = (v >> (bits - 1)) & 1
                v = ((v << 1) | self.f["CF"]) & mask
                self.f["CF"] = c
            elif reg == 3:  # rcr
                c = v & 1
                v = ((v >> 1) | (self.f["CF"] << (bits - 1))) & mask
                self.f["CF"] = c
            elif reg in (4, 6):  # shl / sal
                self.f["CF"] = (v >> (bits - 1)) & 1
                v = (v << 1) & mask
            elif reg == 5:  # shr
                self.f["CF"] = v & 1
                v = (v >> 1) & mask
            else:  # sar
                sign = v & (1 << (bits - 1))
                self.f["CF"] = v & 1
                v = ((v >> 1) | sign) & mask
        return v

    def _wr(self, addr, size, val):
        if size == 1:
            self.wr8(addr, val)
        else:
            self.wr16(addr, val)

    def _string(self, op):
        size = 1 if op in (0xA4, 0xA6, 0xAA, 0xAC, 0xAE) else 2
        delta = -1 if self.f["DF"] else 1
        seg_src = self.seg_override or "DS"
        if self.rep and self.r_["CX"] == 0:
            return              # REP 前缀 + CX=0：一次都不做（容易漏的关键语义）
        while True:
            si = self.r_["SI"]
            di = self.r_["DI"]
            a_src = self.phys(self.sreg[seg_src], si)
            a_dst = self.phys(self.sreg["ES"], di)
            if op in (0xA4, 0xA5):  # movs
                self._wr(a_dst, size, self._rd(a_src, size))
            elif op in (0xA6, 0xA7):  # cmps
                self._rd(a_src, size)
                self.sub_(self._rd(a_src, size), self._rd(a_dst, size), size)
            elif op in (0xAA, 0xAB):  # stos
                self._wr(a_dst, size, self._getreg(0, size))
            elif op in (0xAC, 0xAD):  # lods
                self._setreg(0, size, self._rd(a_src, size))
            else:  # scas
                self.sub_(self._getreg(0, size), self._rd(a_dst, size), size)
            if op in (0xA4, 0xA5, 0xAA, 0xAB, 0xAC, 0xAD):
                self.setr("SI", si + delta * size) if op in (0xA4, 0xA5, 0xAC, 0xAD) else None
                self.setr("DI", di + delta * size) if op in (0xA4, 0xA5, 0xAA, 0xAB) else None
            else:
                self.setr("SI", si + delta * size)
                self.setr("DI", di + delta * size)
            self.cycles += CYCLES["string"]
            if not self.rep:
                break
            self.setr("CX", (self.r_["CX"] - 1) & 0xFFFF)
            if self.r_["CX"] == 0:
                break
            if op in (0xA6, 0xA7, 0xAE, 0xAF):
                if self.rep == "ne" and self.f["ZF"]:
                    break            # REPNE：相等即停
                if self.rep == "re" and not self.f["ZF"]:
                    break            # REPE：不等即停

    def _flags_word(self):
        v = 0x0002
        for i, k in enumerate(["CF", "PF", "AF", "ZF", "SF", "DF", "IF"]):
            v |= (self.f[k] & 1) << [0, 2, 4, 6, 7, 10, 9][i]
        v |= (self.f["OF"] & 1) << 11
        return v

    def _set_flags_word(self, v):
        self.f["CF"] = v & 1
        self.f["PF"] = (v >> 2) & 1
        self.f["AF"] = (v >> 4) & 1
        self.f["ZF"] = (v >> 6) & 1
        self.f["SF"] = (v >> 7) & 1
        self.f["DF"] = (v >> 10) & 1
        self.f["IF"] = (v >> 9) & 1
        self.f["OF"] = (v >> 11) & 1

    # ================= 装载 =================
    def load_flat(self, data: bytes, org: int = 0x100, seg: int = 0x0700):
        base = self.phys(seg, org)
        self.mem[base:base + len(data)] = data
        self.sreg["CS"] = seg
        self.sreg["DS"] = seg
        self.sreg["ES"] = seg
        self.sreg["SS"] = seg
        self.ip = org
        self.setr("SP", 0xFFFE)
        self.setr("AX", 0)
        self.setr("CX", 0)
        self.setr("DX", 0)
        self.setr("BX", 0)

    def state(self):
        return {k: f"0x{v:04X}" for k, v in self.r_.items()}


class _Exit(Exception):
    def __init__(self, code):
        self.code = code


def run_program(binary: bytes, stdin_text="", org=0x100, max_instr=MAX_INSTR_DEFAULT):
    """跑一个平坦二进制，返回 (stdout, 屏幕文本, CPU 状态, 退出码)。"""
    os_ = Os(stdin_text)
    cpu = CPU(os_, max_instr)
    cpu.load_flat(binary, org=org)
    code = 0
    err = None
    try:
        cpu.run()
    except _Exit as e:
        code = e.code
    except Abort as e:
        err = str(e)
    return {
        "stdout": os_.text(),
        "screen": os_.screen_text(),
        "files": os_.dump_files(),
        "regs": cpu.state(),
        "flags": dict(cpu.f),
        "icount": cpu.icount,
        "cycles": cpu.cycles,
        "exit": code,
        "error": err,
    }


def main(argv):
    import pathlib
    if not argv:
        print(__doc__)
        return 2
    path = pathlib.Path(argv[0])
    stdin_text = ""
    if "--input" in argv:
        stdin_text = argv[argv.index("--input") + 1]
    res = run_program(path.read_bytes(), stdin_text)
    print("stdout:", repr(res["stdout"]))
    print("screen:", repr(res["screen"][:200]))
    if "--regs" in argv:
        print("regs:", res["regs"])
        print("flags:", {k: v for k, v in res["flags"].items() if k != "IF"})
    print("icount:", res["icount"], "cycles:", res["cycles"], "exit:", res["exit"])
    if res["error"]:
        print("ERROR:", res["error"])
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
