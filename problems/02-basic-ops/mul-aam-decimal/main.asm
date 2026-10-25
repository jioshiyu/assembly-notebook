; 1.2 基本运算 —— 8 位无符号乘法 + AAM 十进制拆分
; 作业原意：08H * 07H = 56 → AAM 拆成 AH=5, AL=6，塞进 DX 观察。
; 重写：从 stdin 读两个字节，输出 DX 的 4 位十六进制（AH:AL 原样可见）。
use16
org 100h

start:
    call read_hex8
    mov bl, al
    call read_hex8
    mov cl, al
    mov al, bl
    mul cl                  ; AX = AL * CL
    aam                     ; AH = AL/10, AL = AL%10（十进制拆分）
    mov dx, ax              ; 对应作业的两条 MOV DH,AH / MOV DL,AL
    mov ax, dx
    call put_hex16
    call put_crlf
    call exit_dos

include "../../../shared/io.inc"
