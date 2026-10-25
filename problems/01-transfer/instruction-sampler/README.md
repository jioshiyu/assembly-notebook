# instruction-sampler —— 传送类指令合集（REP MOVSB / PUSH-POP / XLAT / 标志位）

[← 题目总表](../../../docs/problems.md)

**输入**：两个十六进制字节：I（XLAT 查表下标）、A（8 位加法输入）
**输出**：四行：COPY=… PUSH_POP=… XLAT=… ADD=… CF=… OF=… SF=…

## 原版做法
mycode.asm 把四个练习串在一起：REP MOVSB 复制 4 字节、两次 PUSH/POP、XLAT 查表、两次 8 位加法。完全没有输出，只能看寄存器。

## 重写与改进
打包成一个可执行程序，按输入计算并打印四个结果；ADD 之后立刻 SETO 取 OF（再往后 ADC 会覆盖标志位）。

## 关键指令
REP MOVSB / PUSH imm / XLATB / ADC / SETO / SHR

## 测试与边界
- 固定用例 4 组：下标 8 与 10（表长 9，验证回绕）、7FH+1 溢出、FFH+1 全零进位
- 随机对拍：`python shared/check.py problems/01-transfer/instruction-sampler --stress 40`

## 复现
```bash
python shared/check.py problems/01-transfer/instruction-sampler          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/01-transfer/instruction-sampler__instruction-sampler.bin --input "<输入>" --regs
```
