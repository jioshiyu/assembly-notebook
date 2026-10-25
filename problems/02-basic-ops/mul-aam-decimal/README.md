# mul-aam-decimal —— 8 位乘法 + AAM 十进制拆分

[← 题目总表](../../../docs/problems.md)

**输入**：两个十六进制字节
**输出**：AH:AL 的 4 位十六进制

## 原版做法
8 * 7 = 56 → AAM 拆成 AH=5, AL=6 塞进 DX，无输出。

## 重写与改进
读两个字节相乘，AAM 拆分后打印 DX；文档里记下 AAM 只在乘积低字节 < 100 时才是合法 BCD。

## 关键指令
MUL / AAM

## 测试与边界
- 固定用例 4 组：0F*0F=225 → AH=22(16h) 已非 BCD；FF*FF 取低字节为 1
- 随机对拍：`python shared/check.py problems/02-basic-ops/mul-aam-decimal --stress 40`

## 复现
```bash
python shared/check.py problems/02-basic-ops/mul-aam-decimal          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/02-basic-ops/mul-aam-decimal__mul-aam-decimal.bin --input "<输入>" --regs
```
