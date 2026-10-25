; 10.3 宏指令 —— CALCFIBO 宏 + 十进制输出
; 原版 CALCFIBO 对 N=2 会 sub cx,2 → CX=0 → LOOP 变成 65535 次（实测 bug），
; 这里补上 N<=2 的提前返回，并用同样"ADD + XCHG + LOOP"的滚动思路。
use16
org 100h

macro calc_fibo
{
    local next_f, done_f, finish_f
    push cx
    push dx
    cmp cx, 1
    jbe done_f
    cmp cx, 2
    jbe done_f
    mov ax, 1
    mov dx, 1
    sub cx, 2
next_f:
    add ax, dx
    xchg ax, dx
    loop next_f
    mov ax, dx
    jmp finish_f
done_f:
    mov ax, 1
finish_f:
    pop dx
    pop cx
}

start:
    call read_hex16
    mov cx, ax
    calc_fibo
    call print_dec
    call put_crlf
    call exit_dos

; ---- 十进制打印 AX（无前导零）----
print_dec:
    push ax
    push bx
    push cx
    push dx
    mov bx, 10
    xor cx, cx
.div_loop:
    xor dx, dx
    div bx
    push dx
    inc cx
    test ax, ax
    jnz .div_loop
.out_loop:
    pop dx
    add dl, '0'
    mov ah, 2
    int 21h
    loop .out_loop
    pop dx
    pop cx
    pop bx
    pop ax
    ret

include "../../../shared/io.inc"
