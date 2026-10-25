# print-by-stack —— 堆栈传参 + RET n 清栈

[← 题目总表](../../../docs/problems.md)

**输入**：一个词
**输出**：原样回显

## 原版做法
MOV SI,[BP+4] 取一个参数，RET 2 丢参数。

## 重写与改进
传两个参数（地址+长度），用 RET 4 清栈；展示 [BP+4]/[BP+6] 的顺序差异。

## 关键指令
PUSH / MOV BP,SP / RET 4

## 测试与边界
- 固定用例 3 组：16 字符长串（验证 CX 边界）
- 随机对拍：`python shared/check.py problems/05-subroutine/print-by-stack --stress 40`

## 复现
```bash
python shared/check.py problems/05-subroutine/print-by-stack          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/05-subroutine/print-by-stack__print-by-stack.bin --input "<输入>" --regs
```
