# print-hex-subroutine —— 子程序打印 16 位十六进制 + H

[← 题目总表](../../../docs/problems.md)

**输入**：一个十六进制字
**输出**：XXXXH

## 原版做法
ROL BX,4 每轮取高半字节，AND 0Fh 后补 '0' 或加 7 转字母，末尾打 'H'。

## 重写与改进
保留 ROL 思路（不改成查表），只改输入来源；PRINT_HEX 用 PUSH/POP 保护全部寄存器。

## 关键指令
ROL / AND / CMP / LOOP

## 测试与边界
- 固定用例 5 组：9→A 分界、0000H、FFFFH
- 随机对拍：`python shared/check.py problems/05-subroutine/print-hex-subroutine --stress 40`

## 复现
```bash
python shared/check.py problems/05-subroutine/print-hex-subroutine          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/05-subroutine/print-hex-subroutine__print-hex-subroutine.bin --input "<输入>" --regs
```
