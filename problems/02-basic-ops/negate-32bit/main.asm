; 1.3 基本运算 —— 32 位整数取负（用 SBB 把借位扩展成全 1/全 0 掩码）
; 作业原意：A=0FFFBH, A_2=0FFFFH 组成 32 位数 0FFFFFFFBH，程序把它取负。
; 重写：从 stdin 读"低字 高字"，输出取负后的 8 位十六进制。
use16
org 100h

start:
    call read_hex16
    mov bx, ax              ; BX = 低字
    call read_hex16
    mov dx, ax              ; DX = 高字
    mov ax, bx              ; DX:AX = 原数

    mov bx, dx
    add bx, bx
    sbb bx, bx              ; 原版掩码技巧：只有高字 >= 8000h（CF=1）才得到 FFFFh
    ; 上面这招只在"高字是负数"时成立；一般数要用"取反加一"：
    not ax
    not dx
    add ax, 1
    adc dx, 0               ; DX:AX = 0 - 原数（32 位取负）

    mov cx, ax
    mov ax, dx
    call put_hex16          ; 高 16 位
    mov ax, cx
    call put_hex16          ; 低 16 位
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"
