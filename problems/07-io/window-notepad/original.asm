; ===== 原始作业源码（照抄，MASM 语法；由 GBK 转 UTF-8；仅存档对照，不参与编译）=====
CSEG    SEGMENT
        ASSUME  CS:CSEG

; 宏：清屏或上卷窗口
SCROLL  MACRO   N, ULR, ULC, LRR, LRC, ATT
        MOV     AH, 6
        MOV     AL, N
        MOV     CH, ULR
        MOV     CL, ULC
        MOV     DH, LRR
        MOV     DL, LRC
        MOV     BH, ATT
        INT     10H
        ENDM

; 宏：设置光标位置
CURSE   MACRO   CURY, CURX
        MOV     AH, 2
        MOV     DH, CURY
        MOV     DL, CURX
        MOV     BH, 0
        INT     10H
        ENDM


; 子程序：在窗口内换行（光标下移，若已在最后一行则上卷）
; 入口：无，使用当前光标位置
; 出口：BX 清零（主程序使用 BX 记录当前行字符数）

NEWLINE PROC
        PUSH    AX
        PUSH    DX

        ; 获取当前光标位置
        MOV     AH, 3
        MOV     BH, 0
        INT     10H             ; DH=行号, DL=列号

        CMP     DH, 18          ; 是否已在最后一行（内框底部行号18）
        JL      NOT_BOTTOM

        ; 已在底部，上卷内窗口一行
        SCROLL  1, 8, 20, 18, 50, 2FH
        CURSE   18, 20
        JMP     DONE

NOT_BOTTOM:
        INC     DH
        CURSE   DH, 20

DONE:
        MOV     BX, 0           ; 新行已输入字符数为0
        POP     DX
        POP     AX
        RET
NEWLINE ENDP


; 主程序

MAIN    PROC    FAR
        ; 清屏
        SCROLL  0, 0, 0, 24, 79, 07H

        ; 绘制外框（背景品红）
        SCROLL  13, 7, 19, 19, 51, 50H

        ; 绘制内框（绿底白字）
        SCROLL  11, 8, 20, 18, 50, 2FH

        ; 光标定位到内框最后一行第一列 (18,20)
        CURSE   18, 20
        MOV     BX, 0           ; BX = 当前行已输入字符数 (0~30)

GET_CHAR:
        MOV     AH, 0
        INT     16H             ; 等待键盘输入

        CMP     AL, 1BH         ; ESC 键
        JE      EXIT

        CMP     AL, 0DH         ; 回车键
        JE      DO_ENTER

        ;  普通字符
        CMP     BX, 30
        JL      DISPLAY

        ; 已满30字符：先自动换行
        CALL    NEWLINE
        ; 注意：NEWLINE 会重置 BX=0

DISPLAY:
        MOV     AH, 0EH         ; BIOS 电传输出（显示字符，光标右移）
        INT     10H
        INC     BX
        JMP     GET_CHAR

DO_ENTER:
        CALL    NEWLINE         ; 换行，不显示字符
        JMP     GET_CHAR

EXIT:
        SCROLL  0, 0, 0, 24, 79, 07H   ; 清屏
        MOV     AH, 4CH
        INT     21H             ; 返回 DOS
MAIN    ENDP

CSEG    ENDS
        END     MAIN