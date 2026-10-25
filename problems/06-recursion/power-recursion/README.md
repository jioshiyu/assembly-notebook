# power-recursion —— 递归求幂 X^N

[← 题目总表](../../../docs/problems.md)

**输入**：底数 指数（各一个十六进制字节）
**输出**：十进制结果（模 2^16）

## 原版做法
POWER PROC 递归调用自身，每层 MUL BL——只乘 AL 低字节，3^6 就错了。

## 重写与改进
改 16 位 MUL BX（结果按 2^16 取模），保留递归结构；0^0 按递归基返回 1。

## 关键指令
CALL / MUL / DEC

## 测试与边界
- 固定用例 6 组：3^5=243、3^6=729（原版在此错）、2^16 溢出为 0
- 随机对拍：`python shared/check.py problems/06-recursion/power-recursion --stress 40`

## 复现
```bash
python shared/check.py problems/06-recursion/power-recursion          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/06-recursion/power-recursion__power-recursion.bin --input "<输入>" --regs
```
