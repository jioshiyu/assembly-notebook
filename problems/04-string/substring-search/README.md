# substring-search —— REPE CMPSB 朴素子串查找

[← 题目总表](../../../docs/problems.md)

**输入**：haystack needle
**输出**：FOUND / NOT FOUND

## 原版做法
SCASB 先测 haystack 长度，再 REPE CMPSB 逐位比较。注意：原版演示数据 '1COOCOO$' 里其实没有 'COOL'，原版跑出来是 NOT FOUND。

## 重写与改进
改成 stdin 两词；空模式与超长模式都安全返回 NOT FOUND；用例里同时保留「真实数据」和「含目标」两个版本。

## 关键指令
SCASB / REPE CMPSB / JCXZ

## 测试与边界
- 固定用例 6 组：空 haystack、整串相同、模式比串长、重复字符
- 随机对拍：`python shared/check.py problems/04-string/substring-search --stress 40`

## 复现
```bash
python shared/check.py problems/04-string/substring-search          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/04-string/substring-search__substring-search.bin --input "<输入>" --regs
```
