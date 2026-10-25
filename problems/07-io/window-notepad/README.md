# window-notepad —— 带边框的记事窗口（30 字符换行 + 窗口内上卷）

[← 题目总表](../../../docs/problems.md)

**输入**：键盘字符流（0x1B = ESC 结束，\r = 回车）
**输出**：不产生 stdout，比对 80x25 屏幕文本

## 原版做法
SCROLL/CURSE 两个宏画框，INT 16h 读键，INT 10h 0Eh 显示；满 30 字符先换行，到第 18 行就窗口上卷。

## 重写与改进
fasm 宏写法保持（macro scroll / curse），交互与滚动规则完全一致；ref.py 提供 expected_screen() 做屏幕对拍。

## 关键指令
INT 10h 06/02/0Eh / INT 16h / 宏参数

## 测试与边界
- 固定用例 4 组：31 字符回卷、回车后上卷、立即 ESC（整屏空白）
- 随机对拍：`python shared/check.py problems/07-io/window-notepad --stress 40`

## 复现
```bash
python shared/check.py problems/07-io/window-notepad          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/07-io/window-notepad__window-notepad.bin --input "<输入>" --regs
```
