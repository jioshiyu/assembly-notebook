; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H
.DATA
    MSG DB 'HELLO WORLD!$'
    STR DB 'THIS IS A TEST!',0
.CODE
PRINT_AX PROC
    PUSH AX
    PUSH SI  
    MOV SI,AX
    MOV AH,2
NEXT_CHAR:
    MOV AL,[SI]
    CMP AL,'!'
    JE EXIT_PRINT
    MOV DL,AL
    INT 21H
    INC SI
    JMP NEXT_CHAR

EXIT_PRINT:    
    POP SI
    POP AX
    RET
PRINT_AX ENDP

START:
    MOV AX,@DATA
    MOV DS,AX
              
    LEA AX,STR
    CALL PRINT_AX
    
    MOV AH,4CH
    INT 21H          
    
END START
