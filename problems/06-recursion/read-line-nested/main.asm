; 7.1 子程序嵌套 —— 整行读入（READSTRING → READCHAR）再回显
; 原版用 AH=01 逐字符读到 CR；这里保留"子程序调子程序"的结构，
; 但读到 LF/CR 为止、并保留空格（比单词读入更接近原版）。
use16
org 100h

start:
    mov di, buf
    call read_line          ; 子程序 A
    mov si, buf
    call print_ptr          ; 子程序 B
    call put_crlf
    call exit_dos

; ---- A：读一整行到 DI，返回 CX=长度（内部调用读字符）----
read_line:
    push ax
    xor cx, cx
.loop:
    call read_char          ; 嵌套调用
    cmp al, 0Dh
    je .done
    cmp al, 0Ah
    je .done
    stosb
    inc cx
    jmp .loop
.done:
    pop ax
    ret

; ---- 读一个字符（不回显）----
read_char:
    mov ah, 8
    int 21h
    ret

; ---- B：打印 SI 起始、CX 个字符 ----
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
