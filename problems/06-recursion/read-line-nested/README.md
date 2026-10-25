# read-line-nested —— 子程序嵌套：整行读入并回显

[← 题目总表](../../../docs/problems.md)

**输入**：一整行（保留空格）
**输出**：原样回显

## 原版做法
READSTRING 调 READCHAR，遇 CR 停，末尾补 $。

## 重写与改进
支持 CR/LF 两种行尾；读字符改成 AH=08h（不回显），这样 stdout 只有程序输出，便于比对。

## 关键指令
CALL / STOSB / CMP

## 测试与边界
- 固定用例 4 组：带空格、前导空格不丢、数字串
- 随机对拍：`python shared/check.py problems/06-recursion/read-line-nested --stress 40`

## 复现
```bash
python shared/check.py problems/06-recursion/read-line-nested          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/06-recursion/read-line-nested__read-line-nested.bin --input "<输入>" --regs
```
