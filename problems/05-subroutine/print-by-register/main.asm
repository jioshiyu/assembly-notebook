; 6.1.1 子程序设计 —— 寄存器传参
; 原版把字符串地址放在 AX 里、遇到 '!' 停；这里改成"地址 + 长度"两个寄存器传参，
; 子程序 print_ptr 只依赖 SI/CX，和调用点解耦，便于复用与测试。
use16
org 100h

start:
    mov di, buf
    call read_word          ; CX = 长度，buf 里是字符
    mov si, buf
    call print_ptr          ; 寄存器传参：SI=地址, CX=长度
    call put_crlf
    call exit_dos

; ---- 子程序：打印 SI 起始、CX 个字符 ----
print_ptr:
    jcxz .ret
.loop:
    mov dl, [si]
    mov ah, 2
    int 21h
    inc si
    loop .loop
.ret:
    ret

include "../../../shared/io.inc"

buf db 128 dup(0)
