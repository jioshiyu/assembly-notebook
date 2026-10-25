# addressing-modes —— 六种寻址方式演示

[← 题目总表](../../../docs/problems.md)

**输入**：一个十六进制字
**输出**：六行：1 IMMEDIATE=… … 6 BASED_INDEXED=…

## 原版做法
逐个演示立即数/寄存器/直接/间接/相对/基址变址，打印 Before/After/Source 三行（输出很长）。

## 重写与改进
每次把结果写进 BUF 再打印「模式名=结果」，输出压缩成 6 行，便于对拍；六种寻址的相对/基址组合保持原样。

## 关键指令
MOV 的六种寻址：[SI] [SI+2] [BX+SI]

## 测试与边界
- 固定用例 3 组：全 0、1234、AAAA（验证各模式取到同一个值）
- 随机对拍：`python shared/check.py problems/08-macro/addressing-modes --stress 40`

## 复现
```bash
python shared/check.py problems/08-macro/addressing-modes          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/08-macro/addressing-modes__addressing-modes.bin --input "<输入>" --regs
```
