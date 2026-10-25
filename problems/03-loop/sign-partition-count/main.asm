; 4.1 循环结构 —— 把数组按符号分成两个数组并计数
; 重写：从 stdin 读 N 和 N 个带符号字节（十六进制，如 FB = -5），
; 输出"非负个数 负数个数"（各 2 位十六进制），对应原版的两个计数器。
use16
org 100h

start:
    call read_hex8
    mov [count], al
    mov byte [cnt_p], 0
    mov byte [cnt_n], 0

    mov cl, [count]
    xor ch, ch
    test cx, cx
    jz done

read_loop:
    call read_hex8
    cmp al, 0
    jl is_neg
    inc byte [cnt_p]
    jmp next
is_neg:
    inc byte [cnt_n]
next:
    loop read_loop

done:
    mov al, [cnt_p]
    call put_hex8
    mov dl, ' '
    mov ah, 2
    int 21h
    mov al, [cnt_n]
    call put_hex8
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

count db 0
cnt_p db 0
cnt_n db 0
