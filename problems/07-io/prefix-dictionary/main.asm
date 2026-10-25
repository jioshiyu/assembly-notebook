; 9.2 输入输出程序设计 —— 单词字典（有序插入 + 前缀查找）
;
; 原版是磁盘驻留版本：DICT.TXT + 临时文件 + 句柄（INT 21h 3C/3F/40），
; 另有窗口界面与 Press any key 停顿。这里把**存储层换成内存数组**，
; 保留可对拍的核心算法：忽略大小写的比较、有序插入、重复检测、前缀匹配。
;
; 输入：空白分隔的命令流
;   1 <word>     插入（>30 字符 → TOOLONG；重复 → DUP；成功 → OK）
;   2 <prefix>   前缀查找（命中输出 "word word ... "，无命中输出 NONE）
;   3            退出
use16
org 100h

MAIN:
    call open_dict
    jmp main_loop

; ===================== 主循环 =====================
main_loop:
    mov di, buf
    call read_word
    mov al, [buf]
    cmp al, '1'
    je do_insert
    cmp al, '2'
    je do_search
    cmp al, '3'
    je bye
    jmp main_loop

bye:
    mov ah, 4Ch
    int 21h

; ===================== 插入 =====================
do_insert:
    mov di, newword
    mov al, 0
    mov cx, 32
    cld
    rep stosb               ; 清空上一条，保证记录尾部补 0
    mov di, newword
    call read_word
    mov byte [di], 0            ; 补串尾
    cmp cx, 30
    ja too_long

    xor bx, bx                  ; BX = 插入位置
find_pos:
    cmp bx, [count]
    jae found_pos
    mov ax, bx
    call mul32
    mov di, words
    add di, ax
    mov si, newword
    call cmp_ci                 ; AX = -1 / 0 / 1
    cmp ax, 0
    jl found_pos                ; 新词更小 → 插在 BX
    je is_dup
    inc bx
    jmp find_pos

found_pos:                      ; 把 [BX..count-1] 整体右移一格（32 字节/条）
    mov cx, [count]
    dec cx
shift_loop:
    cmp cx, bx
    jl shift_done
    mov ax, cx
    call mul32
    mov si, words
    add si, ax
    mov di, si
    add di, 32
    push cx
    mov cx, 32
    cld
    rep movsb
    pop cx
    dec cx
    jmp shift_loop
shift_done:
    mov ax, bx
    call mul32
    mov di, words
    add di, ax
    mov si, newword
    mov cx, 32
    cld
    rep movsb
    inc word [count]
    call save_dict
    mov dx, msg_ok
    call put_str
    call put_crlf
    jmp main_loop

is_dup:
    mov dx, msg_dup
    call put_str
    call put_crlf
    jmp main_loop

too_long:
    mov dx, msg_long
    call put_str
    call put_crlf
    jmp main_loop

; ===================== 前缀查找 =====================
do_search:
    mov di, prefix
    call read_word
    mov byte [di], 0
    mov [plen], cx
    xor bx, bx
    xor bp, bp                  ; BP = 命中数
se_loop:
    cmp bx, [count]
    jae se_done
    mov ax, bx
    call mul32
    mov si, words
    add si, ax
    mov di, prefix
    mov cx, [plen]
    call prefix_match           ; AX = 0 命中
    test ax, ax
    jnz se_next
    inc bp
    mov ax, bx
    call mul32
    mov si, words
    add si, ax
se_show:
    mov dl, [si]
    test dl, dl
    jz se_end_word
    mov ah, 2
    int 21h
    inc si
    jmp se_show
se_end_word:
    mov dl, ' '
    mov ah, 2
    int 21h
se_next:
    inc bx
    jmp se_loop
se_done:
    test bp, bp
    jz se_none
    call put_crlf
    jmp main_loop
se_none:
    mov dx, msg_none
    call put_str
    call put_crlf
    jmp main_loop

; ===================== 子程序 =====================
; AX = AX * 32（条目定长 32 字节）
mul32:
    shl ax, 1
    shl ax, 1
    shl ax, 1
    shl ax, 1
    shl ax, 1
    ret

; 忽略大小写比较 SI 与 DI（0 结尾）：AX = -1 / 0 / 1
cmp_ci:
.loop:
    mov al, [si]
    mov dl, [di]
    and al, 0DFh
    and dl, 0DFh
    cmp al, dl
    jb .less
    ja .greater
    test al, al
    jz .equal
    inc si
    inc di
    jmp .loop
.less:
    mov ax, 0FFFFh
    ret
.greater:
    mov ax, 1
    ret
.equal:
    xor ax, ax
    ret

; SI=词, DI=前缀, CX=前缀长度 → AX=0 命中 / 1 不命中
prefix_match:
.loop:
    test cx, cx
    jz .hit
    mov al, [si]
    mov dl, [di]
    and al, 0DFh
    and dl, 0DFh
    cmp al, dl
    jne .miss
    inc si
    inc di
    dec cx
    jmp .loop
.hit:
    xor ax, ax
    ret
.miss:
    mov ax, 1
    ret


; ---- 启动：打开 DICT.TXT（不存在就创建），读进 words[] ----
open_dict:
    mov dx, fname
    mov ax, 3D00h
    int 21h
    jnc .got
    mov dx, fname
    mov cx, 0
    mov ah, 3Ch
    int 21h
    jc .done
.got:
    mov [dhandle], ax
    mov bx, ax
    mov cx, 1024
    mov dx, words
    mov ah, 3Fh
    int 21h
    mov [dbytes], ax
    mov bx, [dhandle]
    mov ah, 3Eh
    int 21h
    mov ax, [dbytes]
    mov cl, 5
    shr ax, cl              ; 字节数 / 32 = 记录数
    mov [count], ax
.done:
    ret

; ---- 插入后：把 words[] 覆盖写回 DICT.TXT ----
save_dict:
    mov dx, fname
    mov cx, 0
    mov ah, 3Ch
    int 21h
    jc .done
    mov [dhandle], ax
    mov bx, ax
    mov ax, [count]
    mov cl, 5
    shl ax, cl              ; count * 32
    mov cx, ax
    mov dx, words
    mov ah, 40h
    int 21h
    mov bx, [dhandle]
    mov ah, 3Eh
    int 21h
.done:
    ret

include "../../../shared/io.inc"

count dw 0
plen dw 0
buf db 32 dup(0)
newword db 32 dup(0)
prefix db 32 dup(0)
words db 1024 dup(0)
msg_ok db 'OK$'
msg_dup db 'DUP$'
msg_long db 'TOOLONG$'
msg_none db 'NONE$'
fname db 'DICT.TXT',0
dhandle dw 0
dbytes dw 0
