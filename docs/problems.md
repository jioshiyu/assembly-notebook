# 题目总表与逐题说明（21 题）

> 一栏一题：`分类/目录` · 练什么 · 原版做法 · 重写点 · 关键指令。
> 复现：`python shared/check.py problems/<分类>/<目录> --stress 40`

## 01-transfer

**instruction-sampler**（0.x 伪指令与传送类）
- 练：REP MOVSB 复制、PUSH/POP 后进先出、XLAT 查表、8 位加法标志位
- 原版：`mycode.asm` 四个练习**没有任何输出**，只能看寄存器
- 重写：打包成一个程序，输入 `下标 数值`，输出 `COPY / PUSH_POP / XLAT / ADD+CF/OF/SF`
- 关键：`REP MOVSB`、`PUSH imm`、`XLATB`、`ADC`、`SETO`

## 02-basic-ops

**add-with-carry**（1.1）练 8 位加法进位扩展：`ADD` 出 CF → `ADC` 收进高字节。原版常量 93H/78H，重写读两个字节输出 16 位和。
**mul-aam-decimal**（1.2）练 `MUL` + `AAM` 十进制拆分。重写输出 AH:AL；README 记下"乘积低字节 ≥100 时 AAM 不是合法 BCD"。
**negate-32bit**（1.3）练 32 位取负。**原版 `ADD BX,BX / SBB BX,BX` 拿 CF 当掩码，只在高字最高位为 1 时成立**；重写用取反加一。

## 03-loop

**sign-partition-count**（4.1）循环 + 分支 + 计数：统计非负/负数个数，输出 `非负 负`。
**array-intersection**（4.2）双重循环求交集，保持 A 的顺序；空集输出 `NONE`。
**bubble-sort-string**（4.3）冒泡排序 + `XCHG AL,[SI+1]`；原版用 AH=0A 缓冲读，重写读一个词。

## 04-string

**concat-two-strings**（5.1）`REP MOVSB` 拼接两串 + `STOSB` 补 `$`。
**substring-search**（5.2）`SCASB` 测长 + `REPE CMPSB` 朴素查找。**原版演示数据 `'1COOCOO$'` 里没有 `'COOL'`**，实际输出 NOT FOUND。
**hex-to-decimal**（5.3）`DIV` 逐位取余 + `LODSB/STOSB` 转 ASCII，输出 5 位十进制。

## 05-subroutine

**print-by-register**（6.1.1）寄存器传参：SI=地址、CX=长度。
**print-by-stack**（6.1.2）堆栈传参 + `RET 4` 清栈（原版一个参数 + `RET 2`）。
**print-hex-subroutine**（6.2）子程序打印 16 位十六进制 + `H`，用 `ROL BX,4` 取半字节。
**delete-substring**（6.3）删除第 N 位起 M 个字符；M 超长截断到串尾（对应原版对 DX 的钳制）。

## 06-recursion

**read-line-nested**（7.1）子程序嵌套：`READSTRING` 调 `READCHAR`，整行读入并回显（保留空格）。
**power-recursion**（7.2）递归求幂。**原版 `MUL BL` 只乘低字节，3^6 就错**；重写改 16 位 `MUL BX`（模 2^16）。

## 07-io

**window-notepad**（9.1）带边框记事窗口：30 字符自动换行、窗口内上卷、ESC 退出；**用屏幕文本对拍**。
**prefix-dictionary**（9.2）有序插入 + 去重 + 前缀查找。原版是磁盘字典（DICT.TXT + 临时文件 + 句柄），**重写把存储层换成内存数组**，保留可对拍的核心算法；文件 I/O 未复现（见 roadmap）。

## 08-macro

**bitops-with-macros**（10.1）宏版十六进制输出 + AND/OR/XOR/TEST 四条结果。
**fibonacci-macro**（10.2 实为 10.3）`CALCFIBO` 宏求斐波那契。**原版 N=2 时 `sub cx,2` 使 `LOOP` 变 65535 次**；重写补提前返回。
**addressing-modes**（10.2）六种寻址方式（立即数/寄存器/直接/间接/相对/基址变址）依次写进 BUF 并打印。

> 注：10.2 与 10.3 在原作业目录里文件名与内容错位（`10.2.asm` 是寻址方式演示，`10.3.asm` 是斐波那契），这里按**实际内容**归类，目录名不用原编号。
