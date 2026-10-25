; ===== 原始作业源码（照抄，MASM 语法；由 GBK 转 UTF-8；仅存档对照，不参与编译）=====
.MODEL SMALL
.STACK 100H
.DATA
    RESULT1 DW ?
    RESULT2 DW ?   
    
    MSG1 DB 'F(4) = $'
    MSG2 DB 'F(3) = $'
    NEWLINE DB 0DH,0AH,'$'
    
.CODE
START:
    MOV AX, @DATA
    MOV DS, AX

    ; 宏定义（可放在任何位置，不生成代码）
    CALCFIBO MACRO N
        LOCAL NEXT, DONE, FINISH
        PUSH CX
        PUSH DX
        MOV CX, N
        CMP CX, 1
        JBE DONE
        MOV AX, 1
        MOV DX, 1
        SUB CX, 2
    NEXT:
        ADD AX, DX
        XCHG AX, DX
        LOOP NEXT
        MOV AX, DX
        JMP FINISH
    DONE:
        MOV AX, 1
    FINISH:
        POP DX
        POP CX
    ENDM 

    ;  主程序逻辑 
    CALCFIBO 4
    MOV RESULT1, AX
    
    LEA DX, MSG1
    CALL PRINT_STR
    MOV AX, RESULT1
    CALL PRINT_DEC
    CALL PRINT_NEWLINE
    
    CALCFIBO 3
    MOV RESULT2, AX
    
    LEA DX, MSG2
    CALL PRINT_STR
    MOV AX, RESULT2
    CALL PRINT_DEC
    CALL PRINT_NEWLINE

    ; 程序退出
    MOV AH, 4CH
    INT 21H


PRINT_STR PROC
    MOV AH, 09H
    INT 21H
    RET
PRINT_STR ENDP

PRINT_NEWLINE PROC
    LEA DX, NEWLINE
    CALL PRINT_STR
    RET
PRINT_NEWLINE ENDP

PRINT_DEC PROC
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    
    MOV BX, 10
    XOR CX, CX
   
DIV_LOOP:
    XOR DX, DX
    DIV BX
    PUSH DX
    INC CX
    TEST AX, AX
    JNZ DIV_LOOP
    
PRINT_LOOP:
    POP DX
    ADD DL, '0'
    MOV AH, 02H
    INT 21H
    LOOP PRINT_LOOP
    
    POP DX
    POP CX
    POP BX
    POP AX
    RET
PRINT_DEC ENDP

END START