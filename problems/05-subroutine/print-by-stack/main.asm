; 6.1.2 子程序设计 —— 堆栈传参 + RET n 清栈
; 原版用 [BP+4] 取一个参数并 RET 2；这里传"地址 + 长度"两个参数、用 RET 4 清栈，
; 子程序自己负责平衡栈，调用点不用 ADD SP。
use16
org 100h

start:
    mov di, buf
    call read_word
    mov ax, buf
    push ax                 ; 参数 1：缓冲区地址
    push cx                 ; 参数 2：长度
    call print_stack
    call put_crlf
    call exit_dos

; ---- 子程序：从堆栈取参数并打印 ----
print_stack:
    push bp
    mov bp, sp
    push ax
    push si
    push cx
    mov si, [bp+4]          ; 最后压入的是长度（[bp+4]），先压的是地址（[bp+6]）
    mov cx, [bp+6]
    xchg si, cx             ; 交换回来：SI=地址, CX=长度
    jcxz .done
.loop:
    mov dl, [si]
    mov ah, 2
    int 21h
    inc si
    loop .loop
.done:
    pop cx
    pop si
    pop ax
    pop bp
    ret 4                   ; 丢掉两个参数

include "../../../shared/io.inc"

buf db 128 dup(0)
