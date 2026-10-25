; 0.x 伪指令与传送类指令 —— 四个小练习打包成可对拍的程序
; 原版（mycode.asm）没有任何输出，只能靠看寄存器；这里把每个练习的结果打印出来：
;   1) REP MOVSB 把 4 字节数据表复制到 DEST
;   2) PUSH/POP 后进先出：先压 0435H 再压 5C79H，两次 POP 后 AX=0435H
;   3) XLAT 查表：table[I]（I 由输入给出，9 项表循环取）
;   4) 8 位加法 + 标志位：A + 1，输出结果与 CF/OF/SF
use16
org 100h

start:
    call read_hex8
    mov [idx], al           ; 查表下标
    call read_hex8
    mov [num], al           ; 加法输入

    ; ---- 1) REP MOVSB ----
    mov si, mydata
    mov di, dest
    mov cx, 4
    cld
    rep movsb

    ; ---- 2) PUSH / POP ----
    push 0435h
    push 5c79h
    pop ax
    pop ax                  ; AX = 0435h（后进先出）
    mov [pushed], ax

    ; ---- 3) XLAT ----
    mov bx, table
    mov al, [idx]
    xor ah, ah
    mov cl, 9
    div cl                  ; AX / 9 → 商在 AL，余数在 AH
    mov al, ah              ; 取余数当表下标（0..8）
    xlatb
    mov [xlatv], al

    ; ---- 4) 8 位加法 + 标志 ----
    mov al, [num]
    mov bl, 1
    add al, bl
    mov [sum], al
    mov al, 0
    seto al                 ; 80186+：立刻取 OF（后面 adc 会重写标志）
    mov [of], al
    mov al, 0
    adc al, 0               ; AL = CF（CF 仍来自上面的 add）
    mov [cf], al
    mov al, [sum]
    and al, 80h
    mov cl, 7
    shr al, cl              ; 归一化成 0/1
    mov [sf], al

    ; ---- 输出 ----
    mov dx, m_copy
    call put_str
    mov al, [dest]
    call put_hex8
    mov al, [dest+1]
    call put_hex8
    mov al, [dest+2]
    call put_hex8
    mov al, [dest+3]
    call put_hex8
    call put_crlf

    mov dx, m_push
    call put_str
    mov ax, [pushed]
    call put_hex16
    call put_crlf

    mov dx, m_xlat
    call put_str
    mov al, [xlatv]
    call put_hex8
    call put_crlf

    mov dx, m_add
    call put_str
    mov al, [sum]
    call put_hex8
    mov dx, m_cf
    call put_str
    mov al, [cf]
    call put_hex8
    mov dx, m_of
    call put_str
    mov al, [of]
    call put_hex8
    mov dx, m_sf
    call put_str
    mov al, [sf]
    call put_hex8
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"

mydata db 12h, 34h, 56h, 78h
dest db 4 dup(0)
table db 18h, 34h, 05h, 06h, 09h, 0Ah, 0Ch, 11h, 12h
idx db 0
num db 0
pushed dw 0
xlatv db 0
sum db 0
cf db 0
of db 0
sf db 0
m_copy db 'COPY=$'
m_push db 'PUSH_POP=$'
m_xlat db 'XLAT=$'
m_add db 'ADD=$'
m_cf db ' CF=$'
m_of db ' OF=$'
m_sf db ' SF=$'
