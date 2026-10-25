; 4.2 循环结构 —— 求两个数组的交集（保持 A 的顺序）
; 重写：从 stdin 读 "N A元素... M B元素..."，输出交集元素（2 位十六进制，逐个加空格），
; 没有交集则输出 NONE。原版固定 5+5 个字符，这里改成可变长度。
use16
org 100h

start:
    call read_hex8
    mov [an], al
    mov cl, al
    xor ch, ch
    mov di, bufa
    call read_bytes

    call read_hex8
    mov [bn], al
    mov cl, al
    xor ch, ch
    mov di, bufb
    call read_bytes

    mov byte [hits], 0
    mov si, bufa
    mov cl, [an]
    xor ch, ch

outer:
    test cx, cx
    jz finish
    mov al, [si]
    push cx
    push si
    mov cl, [bn]
    xor ch, ch
    mov di, bufb
inner:
    test cx, cx
    jz no_hit
    cmp al, [di]
    je found
    inc di
    loop inner
    jmp no_hit

found:
    inc byte [hits]
    call put_hex8
    mov dl, ' '
    mov ah, 2
    int 21h

no_hit:
    pop si
    pop cx
    inc si
    loop outer

finish:
    cmp byte [hits], 0
    jne done
    mov dx, msg_none
    call put_str
done:
    call put_crlf
    call exit_dos

; 读 CX 个十六进制字节到 DI
read_bytes:
    test cx, cx
    jz .done
.loop:
    push cx
    call read_hex8
    stosb
    pop cx
    loop .loop
.done:
    ret

include "../../../shared/io.inc"

msg_none db 'NONE$'
an db 0
bn db 0
hits db 0
bufa db 32 dup(0)
bufb db 32 dup(0)
