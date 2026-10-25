; =====================================================================
; 8086 课程作业共用 IO（fasm 语法，use16 / org 100h）
; 用法：主程序里 `include "../../../shared/io.inc"`，然后 call 这些例程。
; 约定：输入按"空白分隔的 token"喂给程序；输出全部走 DOS AH=02/AH=09。
; =====================================================================

; ---- 输出：DX 指向 '$' 结尾字符串 ----
put_str:
    mov ah, 9
    int 21h
    ret

; ---- 输出：AL 的低 4 位当作一个十六进制字符 ----
put_nib:
    push ax
    and al, 0Fh
    add al, 30h
    cmp al, 39h
    jbe .out
    add al, 7
.out:
    mov dl, al
    mov ah, 2
    int 21h
    pop ax
    ret

; ---- 输出：AL >>= 4（8086 没有 C1 立即数移位，用 4 次 shr al,1）----
shr4:
    shr al, 1
    shr al, 1
    shr al, 1
    shr al, 1
    ret

; ---- 输出：BX <<= 4（同上，保持 8086 指令集纯净）----
shl4:
    shl bx, 1
    shl bx, 1
    shl bx, 1
    shl bx, 1
    ret

; ---- 输出：AL 作为 2 位十六进制 ----
put_hex8:
    push ax
    call shr4
    call put_nib
    pop ax
    call put_nib
    ret

; ---- 输出：AX 作为 4 位十六进制 ----
put_hex16:
    push ax
    mov al, ah
    call put_hex8
    pop ax
    call put_hex8
    ret

; ---- 输出：换行 ----
put_crlf:
    push ax
    push dx
    mov dl, 0Dh
    mov ah, 2
    int 21h
    mov dl, 0Ah
    mov ah, 2
    int 21h
    pop dx
    pop ax
    ret

; ---- 输入：把一个字符转成 0..15，非法时 CF=1 ----
hex_val:
    cmp al, '0'
    jb .bad
    cmp al, '9'
    jbe .dig
    cmp al, 'A'
    jb .lower
    cmp al, 'F'
    jbe .upper
.lower:
    cmp al, 'a'
    jb .bad
    cmp al, 'f'
    ja .bad
    sub al, 'a' - 10
    clc
    ret
.upper:
    sub al, 'A' - 10
    clc
    ret
.dig:
    sub al, '0'
    clc
    ret
.bad:
    stc
    ret

; ---- 输入：读一个十六进制字节 -> AL，CF=1 表示没读到 ----
; 连续读十六进制字符，遇到非十六进制字符（空格/回车/结尾）停下。
read_hex8:
    push bx
    push cx
    xor bx, bx
    xor cx, cx
.rd:
    mov ah, 8
    int 21h
    call hex_val
    jc .done
    call shl4
    or bl, al
    inc cx
    jmp .rd
.done:
    mov ax, bx
    test cx, cx
    jz .empty
    clc
    pop cx
    pop bx
    ret
.empty:
    stc
    pop cx
    pop bx
    ret

; ---- 输入：读一个十六进制字 -> AX ----
read_hex16:
    push bx
    push cx
    xor bx, bx
    xor cx, cx
.rd:
    mov ah, 8
    int 21h
    call hex_val
    jc .done
    call shl4
    or bl, al
    inc cx
    jmp .rd
.done:
    mov ax, bx
    test cx, cx
    jz .empty
    clc
    pop cx
    pop bx
    ret
.empty:
    stc
    pop cx
    pop bx
    ret

; ---- 输入：读一个"词"到 DI 缓冲区（空白分隔），返回 CX = 长度 ----
read_word:
    push ax
    xor cx, cx
.skip:
    mov ah, 8
    int 21h
    cmp al, 20h
    je .skip
    cmp al, 0Dh
    je .skip
    cmp al, 0Ah
    je .skip
.take:
    cmp al, 20h
    je .done
    cmp al, 0Dh
    je .done
    cmp al, 0Ah
    je .done
    mov [di], al
    inc di
    inc cx
    mov ah, 8
    int 21h
    jmp .take
.done:
    pop ax
    ret

; ---- 程序退出：AL=退出码 ----
exit_dos:
    mov ah, 4Ch
    int 21h
