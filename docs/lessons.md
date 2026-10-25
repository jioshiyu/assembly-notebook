# 经验与坑（全部实测，不是猜的）

## 工具链

1. **fasm 默认按 80386 编码**：`shl bx, 4` → `C1 E3 04`。模拟器按 8086 子集实现时会报"未实现 0xC1"。要 8086 纯指令就用 4 次 `shl bx, 1`（`shared/io.inc` 的 `shl4`/`shr4`）。
2. **`include` 是就地展开**：放在文件开头会让被包含的例程占据 `org 100h` 的入口，程序从 `put_str` 开始跑，几分钟都查不出原因。约定：**include 一律放最后**。
3. **fasm 的 `lea di, label` 非法**，报 `invalid operand`；用 `mov di, label`。
4. **沙箱里子进程不能用管道**：`subprocess.run(capture_output=True)` 直接 `PermissionError`。`shared/fasm.py` 把 fasm 的 stdout 重定向到 `build/*.log` 再读文件。
5. **windows 下 python 在临时目录 mkdir 会被拒**（WinError 5，本机沙箱/DEFENDER 限制），所以测试不要依赖 `tempfile`，构建产物统一落 `build/`。

## 模拟器本身

6. **`jmp/call rel` 的基准是"取完操作数之后的 IP"**：写成 `self.ip = self.ip + self.fetch8()` 会因为求值顺序拿错基准（先算 ip 再取立即数），跳转落到指令中间，症状是"未实现的指令 0x??"。正确写法：先 `rel = self.fetch8()`，再 `self.ip += rel`。
7. **REPE 与 REPNE 的停止条件相反**：`REPE CMPSB`（F3）在 **ZF=0** 时停，`REPNE`（F2）在 **ZF=1** 时停。只判一边会让子串查找永远返回 FOUND。
8. **`JCXZ` 不改 CX**，其余 `LOOP` 家族都要先减再判。
9. 8 位寄存器必须按 **索引** 映射（AL,CL,DL,BL,AH,CH,DH,BH），不能拿名字哈希表直接用 modrm 的 reg 号。
10. `LEA` 要返回**偏移**而不是物理地址——`_ea()` 里顺手记一个 `_last_off` 最省事。

## 判题与用例

11. **用例里的 `expect` 要独立写**（不要拿 ref 生成），否则 ref 错了永远发现不了。本次靠这条抓到 3 处自己写错的期望值（`0F 0F` 的 AAM 结果、`0000 8000` 的取负、作业原题的正负数计数）。
12. **输入必须以换行结尾**：`read_hex8` 靠"读到非十六进制字符"判断 token 结束，输入耗尽时模拟器会抛 `input exhausted`。
13. **空 token 读不出来**：`read_word` 会跳过空白，所以随机生成器至少要给 1 个字符，否则""永远读不到。
14. 边界清单（沿用算法仓库）：0/1 个元素、最大最小值、进位与借位、补码回绕（`0x80000000` 取负还是自己）。

## 原版作业里的问题（写下来当成教材）

15. `1.3` 的 `ADD BX,BX / SBB BX,BX` 用 **CF 当掩码**，只有高字最高位为 1 才能得到 `FFFFh`；一般数要老老实实"取反加一"。
16. `5.2` 演示数据 `'1COOCOO$'` 不含 `'COOL'`，原版实际输出 NOT FOUND。
17. `1.2` 的 AAM 只在乘积低字节 < 100 时是合法 BCD；`0xFF*0xFF` 会得到 `AH=0, AL=1`。
