; 5.3 串指令 —— 16 位十六进制数转 5 位 ASCII 十进制（BCD 练习）
; 重写要点：原版 NUM 写死 8C5Eh；这里从 stdin 读一个十六进制字，
; 仍用 DIV BX 逐位取余 + LODSB/STOSB 转 ASCII，输出 5 位数字（前导零补齐）。
use16
org 100h

start:
    call read_hex16

    mov di, dig
    add di, 4               ; 从个位开始往前写
    mov cx, 5
conv:
    xor dx, dx
    mov bx, 10
    div bx                  ; AX = 商, DX = 余数
    mov [di], dl
    dec di
    loop conv

    mov si, dig
    mov di, asc
    mov cx, 5
    cld
asc_loop:
    lodsb
    add al, '0'
    stosb
    loop asc_loop
    mov al, '$'
    stosb

    mov dx, asc
    call put_str
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

dig db 5 dup(0)
asc db 8 dup(0)
