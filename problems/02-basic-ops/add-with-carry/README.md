# add-with-carry —— 8 位加法 + ADC 进位扩展

[← 题目总表](../../../docs/problems.md)

**输入**：两个十六进制字节
**输出**：4 位十六进制和（16 位）

## 原版做法
常量 93H/78H 相加，MOV DL,AL + MOV DH,0 + ADC DH,0 把进位收进高字节，无输出。

## 重写与改进
读两个字节，用同样的 ADD+ADC 得到 16 位和并打印；保留进位扩展这个练习点。

## 关键指令
ADD / ADC / MOV

## 测试与边界
- 固定用例 5 组：FF+01 进位、0F+0F 半字节进位（AF）
- 随机对拍：`python shared/check.py problems/02-basic-ops/add-with-carry --stress 40`

## 复现
```bash
python shared/check.py problems/02-basic-ops/add-with-carry          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/02-basic-ops/add-with-carry__add-with-carry.bin --input "<输入>" --regs
```
