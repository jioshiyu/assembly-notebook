; 10.1 宏指令 —— 位操作 + 宏版十六进制输出
; 原版用 DATA1/DATA2 常量演示 AND/OR/XOR/TEST，并定义了三个宏；
; 这里保留宏（PRINT_STR / PRINT_HEX_WORD），数据改成 stdin 输入，输出四行结果。
use16
org 100h

macro print_str ptr
{
    mov dx, ptr
    mov ah, 9
    int 21h
}

macro print_hex_word
{
    local next_hex, num_digit
    push ax
    push bx
    push cx
    push dx
    mov bx, ax
    mov cx, 4
next_hex:
    rol bx, 4
    mov dl, bl
    and dl, 0Fh
    cmp dl, 9
    jbe num_digit
    add dl, 7
num_digit:
    add dl, '0'
    mov ah, 2
    int 21h
    loop next_hex
    mov dl, 'H'
    mov ah, 2
    int 21h
    pop dx
    pop cx
    pop bx
    pop ax
}

start:
    call read_hex16
    mov [d1], ax
    call read_hex16
    mov [d2], ax

    print_str msg_and
    mov ax, [d1]
    and ax, [d2]
    print_hex_word
    call put_crlf

    print_str msg_or
    mov ax, [d1]
    or ax, [d2]
    print_hex_word
    call put_crlf

    print_str msg_xor
    mov ax, [d1]
    xor ax, [d2]
    print_hex_word
    call put_crlf

    print_str msg_test
    mov ax, [d1]
    test ax, [d2]           ; TEST 只改标志位，AX 不变
    print_hex_word
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

d1 dw 0
d2 dw 0
msg_and db 'AND=$'
msg_or db 'OR=$'
msg_xor db 'XOR=$'
msg_test db 'TEST=$'
