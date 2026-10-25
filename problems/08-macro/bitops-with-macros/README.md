# bitops-with-macros —— 宏指令：位操作 + 宏版十六进制输出

[← 题目总表](../../../docs/problems.md)

**输入**：两个十六进制字
**输出**：AND=…H / OR=…H / XOR=…H / TEST=…H

## 原版做法
PRINT_STR / PRINT_NEWLINE / PRINT_HEX_WORD 三个宏；数据是常量 1234H 与 00FFH。

## 重写与改进
保留三个宏（PRINT_HEX_WORD 用 fasm local 标签，可多次实例化），输入改成 stdin；TEST 只改标志位，所以输出仍是第一个操作数。

## 关键指令
AND / OR / XOR / TEST / ROL

## 测试与边界
- 固定用例 4 组：1234 ∧ 00FF、全 0、全 1、互补掩码
- 随机对拍：`python shared/check.py problems/08-macro/bitops-with-macros --stress 40`

## 复现
```bash
python shared/check.py problems/08-macro/bitops-with-macros          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/08-macro/bitops-with-macros__bitops-with-macros.bin --input "<输入>" --regs
```
