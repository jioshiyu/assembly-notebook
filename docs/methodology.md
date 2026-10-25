# 方法论：把汇编作业变成可验证项目

> 沉淀自 2026-10-25「桌面 8 个实验 / 21 个 .asm → assembly-notebook」实战。

## 1. 七步流程（每道题固定动作）

1. **读原版**：看清它到底在算什么（很多作业**没有输出**，只有寄存器终态 → 必须自己定义"什么算对"）；
2. **定语义**：写出标准 I/O 约定（见第 2 节），把它变成 `stdin → stdout` 的纯函数；
3. **写参考模型** `tests/ref.py`：用 Python 独立实现同一个语义（不照抄汇编思路，防"同错"）；
4. **写固定用例** `tests/cases.json`：作业原题数值必进，再补 0/最大/进位/回绕等边界；
5. **写重写版** `main.asm`：fasm 语法 + `shared/io.inc`，保持原版想练的指令（ADD/ADC、REP MOVSB…），只把输入输出标准化；
6. **跑质检**：`python shared/check.py <题> --stress 40`，红了先怀疑自己的期望值；
7. **写题目 README**：题意 → 原版做法 → 重写点 → 关键指令 → 边界 → 复现命令。

## 2. I/O 约定（全仓库统一，别每题自创）

- 输入：空白分隔的 **十六进制 token**（`read_hex8` / `read_hex16` / `read_word`），**行尾必须有换行**，否则读不到结束符；
- 输出：全部走 `put_str` / `put_hex8` / `put_hex16` / `put_crlf`，**结尾一律 CRLF**；
- 读键用 `INT 21h AH=08h`（不回显），这样 stdout 只有程序自己打印的内容，才能直接比对；
- 程序以 `INT 21h AH=4Ch` 退出，退出码默认 0。

## 3. fasm 写法约定（踩过才知道）

- `use16` + `org 100h`，不写 `format`，直接出平坦二进制；
- **`include` 必须放在入口代码之后**：include 是就地展开，放文件开头会把 `0x100` 的入口抢走；
- 引用标号用 `mov di, label`（fasm 的 `lea di, label` 非法，`lea di, [label]` 虽可但没必要）；
- fasm 默认按 80386 编码：`shl bx, 4` 会生成 `C1`（80186+）。课程要 8086 纯指令时用 `shl4` / `shr4` 这种 **1 位重复移位**；
- 数据用 `db 64 dup(0)`（`rb` 在平坦二进制里语义不清）。

## 4. 如何加一道新题

```bash
mkdir -p problems/05-subroutine/print-string-through-stack/tests
# 写 main.asm / original.asm / tests/ref.py / tests/cases.json
python shared/check.py problems/05-subroutine/print-string-through-stack --stress 40
```

`ref.py` 必须提供 `expected(stdin_text) -> str`，可选 `gen(rng) -> str`（没有就跳过对拍）。

## 5. 什么时候该怀疑"原版是错的"

原版很多是课堂练习，**不保证正确**。已确认的例子：

- `1.3` 的 `SBB BX,BX` 掩码技巧只在**高字最高位为 1**时成立（CF 当掩码），一般数会得到错答案；
- `5.2` 的演示数据 `'1COOCOO$'` 里其实**没有** `'COOL'`，原版跑出来是 NOT FOUND；
- `1.2` 的 AAM 在乘机 > 99 时给出非 BCD 结果（AH 会 > 9）。

处理原则：**重写版按语义写对**，README 里写清"原版哪里不对、为什么"，不要把 bug 也复制过来。
