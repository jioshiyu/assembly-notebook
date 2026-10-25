; 6.2 子程序设计 —— 打印 16 位十六进制数（ROL 4 逐半字节取数 + 'H' 结尾）
; 原版 NUM 写死 1000110001011110B；这里从 stdin 读一个十六进制字，
; 打印逻辑沿用原版子程序思路（ROL BX,4 / AND 0Fh / 补 '7' 跳字母）。
use16
org 100h

start:
    call read_hex16
    call print_hex          ; AX → 4 位十六进制 + 'H'
    call put_crlf
    call exit_dos

; ---- 子程序：AX → "XXXXH" ----
print_hex:
    push ax
    push bx
    push cx
    push dx
    mov bx, ax
    mov cx, 4
.next:
    rol bx, 4
    mov dl, bl
    and dl, 0Fh
    cmp dl, 10
    jl .digit
    add dl, 7
.digit:
    add dl, '0'
    mov ah, 2
    int 21h
    loop .next
    mov dl, 'H'
    mov ah, 2
    int 21h
    pop dx
    pop cx
    pop bx
    pop ax
    ret

include "../../../shared/io.inc"
