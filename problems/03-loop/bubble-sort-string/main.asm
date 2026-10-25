; 4.3 循环结构 —— 冒泡排序一个字符串（ASCII 升序）
; 重写：原版用 AH=0A 缓冲读入 80 字符再排序；这里读一个词（测试友好），
; 排序仍是经典双层循环 + 条件交换（XCHG AL,[SI+1]）。
use16
org 100h

start:
    mov di, buf
    call read_word
    mov [len], cx

    mov cx, [len]
    cmp cx, 1
    jbe print_it            ; 0/1 个字符无需排序
    dec cx
outer:
    push cx
    mov si, buf
    mov cx, [len]
    dec cx
inner:
    mov al, [si]
    cmp al, [si+1]
    jle noswap
    xchg al, [si+1]
    mov [si], al
noswap:
    inc si
    loop inner
    pop cx
    loop outer

print_it:
    mov si, buf
    mov cx, [len]
    test cx, cx
    jz done
disp:
    mov dl, [si]
    mov ah, 2
    int 21h
    inc si
    loop disp
done:
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

len dw 0
buf db 128 dup(0)
