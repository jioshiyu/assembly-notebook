# prefix-dictionary —— 单词字典：有序插入 + 去重 + 前缀查找 + 磁盘持久化

[← 题目总表](../../../docs/problems.md)

**输入**：命令流：1 词 / 2 前缀 / 3 退出
**输出**：每条命令一行：OK / DUP / TOOLONG，或命中词列表 / NONE

## 原版做法
897 行的磁盘字典：DICT.TXT + 临时文件交替改写 + 窗口界面 + Press any key。

## 重写与改进
存储层改成定长 32 字节记录 + 内存虚拟盘：启动 3Dh/3Ch 打开，3Fh 读入，插入后 3Ch 截断 + 40h 整表写回，3Eh 关闭。算法核心（忽略大小写比较、有序插入、去重、前缀匹配）保留；UI 层简化成命令行。

## 关键指令
CMP（忽略大小写）/ REP MOVSB / INT 21h 3C 3D 3E 3F 40 41 42

## 测试与边界
- 固定用例 5 组：重复词（大小写不同）、空字典、31 字符超长、expected_disk 同时校验 DICT.TXT 内容
- 随机对拍：`python shared/check.py problems/07-io/prefix-dictionary --stress 40`

## 复现
```bash
python shared/check.py problems/07-io/prefix-dictionary          # 编译 + 固定用例 + 对拍
python shared/asm86.py build/07-io/prefix-dictionary__prefix-dictionary.bin --input "<输入>" --regs
```
