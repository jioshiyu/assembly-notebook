# delete-substring —— 删除第 N 位起的 M 个字符

[← 题目总表](../../../docs/problems.md)

**输入**：字符串 N M（N 从 1 开始）
**输出**：删除后的字符串

## 原版做法
堆栈传 (str,N,M)，内部「保留前 N-1 个 + 从第 N-1+M 个开始拷贝」，M 过大时钳制到串尾。

## 重写与改进
同语义但参数走 stdin；显式处理 N=0 / N 超长 / M 超长三种边界，并写进用例。

## 关键指令
REP MOVSB / CMP / JG

## 测试与边界
- 固定用例 6 组：删首字符、M 超长截断、N=0、N 超长、全同字符
- 随机对拍：`python shared/check.py problems/05-subroutine/delete-substring --stress 40`

## 复现
```bash
python shared/check.py problems/05-subroutine/delete-substring          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/05-subroutine/delete-substring__delete-substring.bin --input "<输入>" --regs
```
