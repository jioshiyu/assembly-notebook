; ===== 原始作业源码（照抄，MASM 语法；由 GBK 转 UTF-8；仅存档对照，不参与编译）=====
.MODEL SMALL
.STACK 100H
.DATA
    DATA1 DW 1234H
    DATA2 DW 00FFH

    MSG1 DB 'AND: 1234H AND 00FFH = $'
    MSG2 DB 'OR:  1234H OR 00FFH = $'
    MSG3 DB 'XOR: 1234H XOR 00FFH = $'
    MSG4 DB 'TEST:1234H TEST 00FFH (flags only) = $'
    NEWLINE DB 13,10,'$'

.CODE
START:
    MOV AX, @DATA
    MOV DS, AX

    ; 宏：显示字符串（DX指向$结尾字符串）
    PRINT_STR MACRO
        MOV AH, 09H
        INT 21H
    ENDM

    ; 宏：显示换行
    PRINT_NEWLINE MACRO
        LEA DX, NEWLINE
        PRINT_STR
    ENDM

    ; 宏：显示 AX 中的十六进制数（4位，带H后缀），不使用任何子程序
    PRINT_HEX_WORD MACRO
        LOCAL NEXT_HEX, NUM_DIGIT
        PUSH AX
        PUSH BX
        PUSH CX
        PUSH DX
        
        MOV BX, AX
        MOV CX, 4
        MOV AH, 02H          ; DOS 单字符输出功能
    NEXT_HEX:
        ROL BX, 4
        MOV DL, BL
        AND DL, 0FH
        CMP DL, 9
        JBE NUM_DIGIT
        ADD DL, 7
    NUM_DIGIT:
        ADD DL, '0'
        INT 21H
        LOOP NEXT_HEX
        
        MOV DL, 'H'          ; 输出后缀 H
        INT 21H
        
        POP DX
        POP CX
        POP BX
        POP AX
    ENDM

    
    ; 1. AND
    LEA DX, MSG1
    PRINT_STR
    MOV AX, DATA1
    AND AX, DATA2
    PRINT_HEX_WORD
    PRINT_NEWLINE

    ; 2. OR
    LEA DX, MSG2
    PRINT_STR
    MOV AX, DATA1
    OR AX, DATA2
    PRINT_HEX_WORD
    PRINT_NEWLINE

    ; 3. XOR
    LEA DX, MSG3
    PRINT_STR
    MOV AX, DATA1
    XOR AX, DATA2
    PRINT_HEX_WORD
    PRINT_NEWLINE

    ; 4. TEST
    LEA DX, MSG4
    PRINT_STR
    MOV AX, DATA1
    TEST AX, DATA2         ; TEST 不影响 AX，所以 AX 仍为 DATA1
    PRINT_HEX_WORD
    PRINT_NEWLINE

    MOV AH, 4CH
    INT 21H
END START