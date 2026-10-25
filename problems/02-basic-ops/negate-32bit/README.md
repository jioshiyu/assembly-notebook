# negate-32bit —— 32 位数取负（掩码技巧 vs 取反加一）

[← 题目总表](../../../docs/problems.md)

**输入**：低字 高字 两个十六进制字
**输出**：取负后的 8 位十六进制

## 原版做法
ADD BX,BX / SBB BX,BX 把 CF 当掩码，再 XOR/SUB 完成取负。这招只在「高字最高位为 1」时成立——一般数会算错。

## 重写与改进
改成「取反加一」（NOT AX / NOT DX / ADD AX,1 / ADC DX,0），对任意 32 位数都正确；README 保留原版思路作为对照。

## 关键指令
NOT / ADD / ADC / SBB（原版）

## 测试与边界
- 固定用例 5 组：0FFFFFFFBh → 5、0x80000000 取负仍是自身、需要借位的数
- 随机对拍：`python shared/check.py problems/02-basic-ops/negate-32bit --stress 40`

## 复现
```bash
python shared/check.py problems/02-basic-ops/negate-32bit          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/02-basic-ops/negate-32bit__negate-32bit.bin --input "<输入>" --regs
```
