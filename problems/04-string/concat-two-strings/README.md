# concat-two-strings —— REP MOVSB 拼接两个字符串

[← 题目总表](../../../docs/problems.md)

**输入**：两个词
**输出**：拼接结果

## 原版做法
REP MOVSB 各拷 5 字节到 DEST，再 STOSB 补 $。

## 重写与改进
长度由输入决定；MOVSB 两段 + STOSB 补结束符的思路不变。

## 关键指令
REP MOVSB / STOSB / CLD

## 测试与边界
- 固定用例 4 组：长度不等、单字符、10 字符长串
- 随机对拍：`python shared/check.py problems/04-string/concat-two-strings --stress 40`

## 复现
```bash
python shared/check.py problems/04-string/concat-two-strings          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/04-string/concat-two-strings__concat-two-strings.bin --input "<输入>" --regs
```
