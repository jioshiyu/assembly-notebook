# array-intersection —— 两个数组求交集（保持 A 的顺序）

[← 题目总表](../../../docs/problems.md)

**输入**：N A元素… M B元素…
**输出**：交集元素（2 位十六进制，逐个带空格）或 NONE

## 原版做法
固定 A~E 与 C~G 两组字符，双重循环比较，命中就存进 BUF。

## 重写与改进
长度可变；输出改成命中即打印 + 末尾 CRLF，空集输出 NONE（原版空集会什么都不打）。

## 关键指令
CMP / JE / LOOP / JCXZ

## 测试与边界
- 固定用例 5 组：空数组、无交集、A 内重复元素保留次数、顺序跟 A 走
- 随机对拍：`python shared/check.py problems/03-loop/array-intersection --stress 40`

## 复现
```bash
python shared/check.py problems/03-loop/array-intersection          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/03-loop/array-intersection__array-intersection.bin --input "<输入>" --regs
```
