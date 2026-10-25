# bubble-sort-string —— 冒泡排序一个字符串

[← 题目总表](../../../docs/problems.md)

**输入**：一个词
**输出**：ASCII 升序排序后的字符串

## 原版做法
INT 21h AH=0A 缓冲读入 80 字符，双层 LOOP + XCHG AL,[SI+1] 交换。

## 重写与改进
读一个词（测试友好），排序逻辑不变；长度 ≤1 直接跳过外层。

## 关键指令
CMP / JLE / XCHG / LOOP

## 测试与边界
- 固定用例 5 组：已有序、完全逆序、大小写混合、单字符
- 随机对拍：`python shared/check.py problems/03-loop/bubble-sort-string --stress 40`

## 复现
```bash
python shared/check.py problems/03-loop/bubble-sort-string          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/03-loop/bubble-sort-string__bubble-sort-string.bin --input "<输入>" --regs
```
