; 7.2 递归 —— 递归求幂 X^N（原版用 MUL BL，只有 8 位，稍大就错）
; 原版：POWER 递归，每层用 MUL BL（只乘 AL 低字节）→ 3^6 就溢出错了。
; 重写：改成 16 位 MUL BX（结果按 2^16 取模），并保留递归结构。
use16
org 100h

start:
    call read_hex8
    mov [base], al
    call read_hex8
    mov cl, al              ; 指数
    mov al, [base]
    call pow                ; AX = base^exp (mod 2^16)
    call print_dec          ; 十进制输出
    call put_crlf
    call exit_dos

; ---- 递归求幂：AX=底数, CX=指数 → AX 结果（模 2^16）----
pow:
    test cx, cx
    jnz .rec
    mov ax, 1
    ret
.rec:
    push ax                 ; 保存本层底数
    push cx
    dec cx
    call pow                ; 递归求 底数^(n-1)
    pop cx
    pop bx                  ; BX = 底数
    mul bx                  ; DX:AX = 底数^(n-1) * 底数
    ret

; ---- 十进制打印 AX（无前导零）----
print_dec:
    push ax
    push bx
    push cx
    push dx
    mov bx, 10
    xor cx, cx
.div_loop:
    xor dx, dx
    div bx
    push dx
    inc cx
    test ax, ax
    jnz .div_loop
.out_loop:
    pop dx
    add dl, '0'
    mov ah, 2
    int 21h
    loop .out_loop
    pop dx
    pop cx
    pop bx
    pop ax
    ret

include "../../../shared/io.inc"

base db 0
