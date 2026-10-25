; 5.2 串指令 —— 用 REPE CMPSB 做朴素子串查找
; 重写要点：原版把 'COOL' 写死在 '1COOCOO$' 里，这里改成 stdin 读两个词
; （haystack needle），输出 FOUND / NOT FOUND，便于随机对拍。
use16
org 100h

start:
    mov di, hay
    call read_word
    mov [hlen], cx
    mov di, pat
    call read_word
    mov [plen], cx

    mov bx, [plen]
    test bx, bx
    jz not_found            ; 空模式：不匹配
    mov cx, [hlen]
    cmp cx, bx
    jb not_found
    sub cx, bx
    inc cx                  ; 候选起点个数
    mov si, hay

search_loop:
    push cx
    push si
    mov di, pat
    mov cx, bx
    cld
    repe cmpsb              ; 逐字节比较，CX 用尽或不等即停
    pop si
    pop cx
    je found
    inc si
    loop search_loop
    jmp not_found

found:
    mov dx, msg_found
    jmp show
not_found:
    mov dx, msg_nf
show:
    call put_str
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

msg_found db 'FOUND$'
msg_nf db 'NOT FOUND$'
hay db 128 dup(0)
pat db 64 dup(0)
hlen dw 0
plen dw 0
