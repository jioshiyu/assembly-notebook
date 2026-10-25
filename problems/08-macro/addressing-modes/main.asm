; 10.2 宏指令 —— 六种寻址方式演示（每种都写进 BUF 再打印，便于对拍）
; 原版逐个打印"Before/After/Source"，这里简化为"模式名=结果"，输入一个数值依次演示。
use16
org 100h

macro show label_ptr
{
    mov dx, label_ptr
    call put_str
    mov ax, [buf]
    call put_hex16
    call put_crlf
}

start:
    call read_hex16
    mov [val], ax

    ; 1 立即数寻址
    mov word [buf], 1234h
    show m1

    ; 2 寄存器寻址
    mov ax, [val]
    mov [buf], ax
    show m2

    ; 3 直接寻址
    mov ax, [val]
    mov [temp], ax
    mov ax, [temp]
    mov [buf], ax
    show m3

    ; 4 寄存器间接寻址
    mov ax, [val]
    mov [array], ax
    mov si, array
    mov ax, [si]
    mov [buf], ax
    show m4

    ; 5 寄存器相对寻址
    mov ax, [val]
    mov si, array
    mov [si+2], ax
    mov ax, [si+2]
    mov [buf], ax
    show m5

    ; 6 基址变址寻址
    mov ax, [val]
    mov bx, array
    mov si, 4
    mov [bx+si], ax
    mov ax, [bx+si]
    mov [buf], ax
    show m6

    call exit_dos

include "../../../shared/io.inc"

buf dw 0
val dw 0
temp dw 5678h
array dw 10 dup(0)
m1 db '1 IMMEDIATE=$'
m2 db '2 REGISTER=$'
m3 db '3 DIRECT=$'
m4 db '4 INDIRECT=$'
m5 db '5 RELATIVE=$'
m6 db '6 BASED_INDEXED=$'
