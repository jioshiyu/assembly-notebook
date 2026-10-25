# fibonacci-macro —— 宏求斐波那契 + 十进制输出

[← 题目总表](../../../docs/problems.md)

**输入**：一个十六进制字 N
**输出**：十进制 F(N)

## 原版做法
CALCFIBO 宏用 ADD AX,DX / XCHG / LOOP 滚动。对 N=2 会 sub cx,2 → CX=0 → LOOP 变 65535 次（死循环）。

## 重写与改进
补 N<=2 提前返回，其余滚动逻辑不变；结果按 16 位取模。

## 关键指令
fasm macro / local / XCHG / LOOP / DIV

## 测试与边界
- 固定用例 7 组：F(2)=1（原版死循环）、F(24)=46368（16 位最大）、F(0) 按宏基返回 1
- 随机对拍：`python shared/check.py problems/08-macro/fibonacci-macro --stress 40`

## 复现
```bash
python shared/check.py problems/08-macro/fibonacci-macro          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/08-macro/fibonacci-macro__fibonacci-macro.bin --input "<输入>" --regs
```
