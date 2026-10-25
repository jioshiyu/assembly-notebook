; 9.1 输入输出程序设计 —— 带边框的"记事窗口"（30 字符自动换行 + 窗口内上卷）
; 原版用 SCROLL/CURSE 两个宏画框，INT 16h 读键，INT 10h 0Eh 显示。
; 这里保持同样的交互，但约定：输入字符流里 0x1B（ESC）结束；输出用屏幕文本比对。
use16
org 100h

macro scroll n, ulr, ulc, lrr, lrc, att
{
    mov ah, 6
    mov al, n
    mov ch, ulr
    mov cl, ulc
    mov dh, lrr
    mov dl, lrc
    mov bh, att
    int 10h
}

macro curse cy, cx_
{
    mov ah, 2
    mov dh, cy
    mov dl, cx_
    mov bh, 0
    int 10h
}

start:
    scroll 0, 0, 0, 24, 79, 07h     ; 清屏
    scroll 13, 7, 19, 19, 51, 50h   ; 外框
    scroll 11, 8, 20, 18, 50, 2fh   ; 内框
    curse 18, 20                    ; 光标到内框最后一行
    mov bx, 0                       ; BX = 当前行已输入字符数

get_char:
    mov ah, 0
    int 16h                         ; 等键
    cmp al, 1bh                     ; ESC
    je exit_prog
    cmp al, 0dh                     ; 回车
    je do_enter
    cmp bx, 30
    jl show_ch
    call newline                    ; 满 30 字符先换行（newline 里会把 BX 清零）

show_ch:
    mov ah, 0eh                     ; BIOS 电传输出
    int 10h
    inc bx
    jmp get_char

do_enter:
    call newline
    jmp get_char

newline:                            ; 窗口内换行：到底部则上卷一行
    push ax
    push dx
    mov ah, 3
    mov bh, 0
    int 10h                         ; DH=行, DL=列
    cmp dh, 18
    jl not_bottom
    scroll 1, 8, 20, 18, 50, 2fh
    curse 18, 20
    jmp nl_done
not_bottom:
    inc dh
    curse dh, 20
nl_done:
    mov bx, 0
    pop dx
    pop ax
    ret

exit_prog:
    mov ah, 4ch
    int 21h
