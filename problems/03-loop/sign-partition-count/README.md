# sign-partition-count —— 按符号分区并计数

[← 题目总表](../../../docs/problems.md)

**输入**：N 个带符号字节（十六进制，FB = -5）
**输出**：非负个数 负数个数（各 2 位十六进制）

## 原版做法
遍历 10 个常量，CMP AL,0 / JL 分成正负两组，两个计数器分别 INC，再 ADD AL,'0' 打印。

## 重写与改进
改成可变长度 + 打印计数；分区逻辑相同，去掉两个临时数组（只保留计数，语义更清楚）。

## 关键指令
CMP / JL / INC / LOOP

## 测试与边界
- 固定用例 5 组：空数组、0 算非负、-128 与 127 边界
- 随机对拍：`python shared/check.py problems/03-loop/sign-partition-count --stress 40`

## 复现
```bash
python shared/check.py problems/03-loop/sign-partition-count          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/03-loop/sign-partition-count__sign-partition-count.bin --input "<输入>" --regs
```
