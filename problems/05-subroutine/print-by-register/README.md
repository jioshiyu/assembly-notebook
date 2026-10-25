# print-by-register —— 寄存器传参的子程序

[← 题目总表](../../../docs/problems.md)

**输入**：一个词
**输出**：原样回显

## 原版做法
PRINT_AX PROC 把地址放 AX，遇 '!' 停。

## 重写与改进
改成 SI=地址、CX=长度 两个寄存器传参，子程序与调用点解耦；原版靠哨兵字符，这里靠长度更安全。

## 关键指令
CALL / RET / CMP / LOOP

## 测试与边界
- 固定用例 3 组：单字符、长串、原题字符串
- 随机对拍：`python shared/check.py problems/05-subroutine/print-by-register --stress 40`

## 复现
```bash
python shared/check.py problems/05-subroutine/print-by-register          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/05-subroutine/print-by-register__print-by-register.bin --input "<输入>" --regs
```
