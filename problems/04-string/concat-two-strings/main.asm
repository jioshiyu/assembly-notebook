; 5.1 串指令 —— 用 MOVSB 把两段字符串拼接到 DEST
; 重写要点：原版写死 'HELLO'/'WORLD'，这里改成从 stdin 读两个词，
; 拼接逻辑仍是 REP MOVSB + STOSB，输出用 DOS AH=09 打印。
use16
org 100h

start:
    mov di, buf1
    call read_word
    mov [len1], cx
    mov di, buf2
    call read_word
    mov [len2], cx

    mov si, buf1
    mov di, dest
    mov cx, [len1]
    cld
    rep movsb               ; 第一段
    mov si, buf2
    mov cx, [len2]
    rep movsb               ; 第二段
    mov al, '$'
    stosb                   ; 补结束符

    mov dx, dest
    call put_str
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

buf1 db 64 dup(0)
buf2 db 64 dup(0)
len1 dw 0
len2 dw 0
dest db 200 dup(0)
