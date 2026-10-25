# hex-to-decimal —— 16 位十六进制转 5 位十进制

[← 题目总表](../../../docs/problems.md)

**输入**：一个十六进制字
**输出**：5 位十进制（前导零补齐）

## 原版做法
DIV BX（BX=10）逐位取余写进 BCD 缓冲，再 LODSB + ADD '0' + STOSB 转 ASCII。

## 重写与改进
输入改成 stdin；输出固定 5 位（和原版缓冲长度一致），便于逐位比对。

## 关键指令
DIV / LODSB / STOSB / LOOP

## 测试与边界
- 固定用例 5 组：0、FFFF（65535）、正好 5 位（10000）
- 随机对拍：`python shared/check.py problems/04-string/hex-to-decimal --stress 40`

## 复现
```bash
python shared/check.py problems/04-string/hex-to-decimal          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/04-string/hex-to-decimal__hex-to-decimal.bin --input "<输入>" --regs
```
