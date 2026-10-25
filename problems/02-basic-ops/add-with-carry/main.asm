; 1.1 基本运算指令 —— 8 位加法 + 进位扩展成 16 位和
; 重写要点：
;   * 原版用常量 93H/78H，没有输出；重写改成从 stdin 读两个字节、打印 4 位十六进制和，
;     这样才有可能对拍（原版语义保持不变，见 original.asm）；
;   * 保留作业想练的两条指令：ADD 产生 CF，ADC 把进位收进高位。
use16
org 100h

start:
    call read_hex8          ; AL = 被加数
    mov bl, al
    call read_hex8          ; AL = 加数
    mov dl, al
    mov al, bl
    add al, dl              ; AL = 低字节和，CF = 进位
    mov ah, 0
    adc ah, 0               ; AH = 进位（对应作业里的 ADC DH,0）
    call put_hex16          ; 打印 16 位和
    call put_crlf
    call exit_dos

; 共用 IO 放在入口之后（include 是就地展开，放前面会抢走 0x100 的入口）
include "../../../shared/io.inc"
