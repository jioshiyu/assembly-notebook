; 6.3 子程序设计 —— 从字符串里删除 N 位置起 M 个字符
; 原版通过堆栈传 (str, N, M)，内部用 "保留前 N-1 个 + 从第 N-1+M 个开始拷贝" 实现；
; 这里保持同一语义（N 从 1 开始），但把参数改成 stdin 输入，便于随机对拍。
use16
org 100h

start:
    mov di, buf
    call read_word
    mov [len], cx           ; 原串长度
    call read_hex8
    mov ah, 0
    mov [npos], ax          ; N
    call read_hex8
    mov ah, 0
    mov [mcnt], ax          ; M

    mov ax, [npos]
    test ax, ax
    jz plain                ; N=0 视为不删
    cmp ax, [len]
    ja plain                ; N 超出长度：不删

    dec ax                  ; startidx = N-1（0 基）
    mov [startidx], ax
    mov bx, [len]
    sub bx, ax              ; 可删上限 = len - startidx
    mov cx, [mcnt]
    cmp cx, bx
    jbe clamp
    mov cx, bx              ; M 过大时截断（对应原版对 DX 的钳制）
clamp:
    mov [mcnt], cx
    add ax, cx
    mov [tailidx], ax

    mov si, buf
    mov di, res
    mov cx, [startidx]
    cld
    rep movsb               ; 头部：前 N-1 个字符
    mov si, buf
    add si, [tailidx]
    mov cx, [len]
    sub cx, [tailidx]
    rep movsb               ; 尾部：跳过被删的 M 个
    mov ax, [len]
    sub ax, [mcnt]
    mov [rlen], ax
    jmp print_res

plain:
    mov si, buf
    mov di, res
    mov cx, [len]
    cld
    rep movsb
    mov ax, [len]
    mov [rlen], ax

print_res:
    mov si, res
    mov cx, [rlen]
    test cx, cx
    jz all_done
disp_lp:
    mov dl, [si]
    mov ah, 2
    int 21h
    inc si
    loop disp_lp

all_done:
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

len dw 0
rlen dw 0
npos dw 0
mcnt dw 0
startidx dw 0
tailidx dw 0
buf db 128 dup(0)
res db 128 dup(0)
