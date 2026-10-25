; ===== 原始作业源码（照抄，MASM 语法，仅存档对照）=====
.MODEL SMALL
.STACK 100H

.DATA
    STR DB 'ABCDEFGHIJKLMNOPQRST$'
    LEN EQU $ - STR - 1      
    N DB 4                   
    M DB 5                 
    MSG1 DB 'ORIGINAL:$'
    MSG2 DB 0DH,0AH,'MODIFIED:$'

.CODE

show PROC
    PUSH AX
    MOV AH, 9
    INT 21H
    POP AX
    RET
show ENDP

DEL_STR PROC
    PUSH BP
    MOV BP, SP
    PUSH AX
    PUSH BX
    PUSH CX
    PUSH DX
    PUSH SI
    PUSH DI

    MOV CX, [BP+6]      
    MOV DX, [BP+4]      
    MOV SI, [BP+8]      
    MOV DI, SI

    CMP CX, LEN
    JG  EXIT_DEL        

    MOV AX, LEN
    SUB AX, CX         
    INC AX              
    CMP DX, AX
    JLE  OK_M
    MOV DX, AX          

OK_M:
    DEC CX              
    ADD SI, CX
    ADD DI, CX

    ADD SI, DX

COPY_LOOP:
    MOV AL, [SI]
    MOV [DI], AL
    CMP AL, '$'
    JE  DONE
    INC SI
    INC DI
    JMP COPY_LOOP

DONE:
    POP DI
    POP SI
    POP DX
    POP CX
    POP BX
    POP AX
    POP BP
    RET 6               

EXIT_DEL:
    POP DI
    POP SI
    POP DX
    POP CX
    POP BX
    POP AX
    POP BP
    RET 6
DEL_STR ENDP

START:
    MOV AX, @DATA
    MOV DS, AX

    LEA DX, MSG1
    CALL show
    LEA DX, STR
    CALL show

    LEA AX, STR
    PUSH AX
    MOV AL, N
    MOV AH, 0
    PUSH AX
    MOV AL, M
    MOV AH, 0
    PUSH AX
    CALL DEL_STR

    LEA DX, MSG2
    CALL show
    LEA DX, STR
    CALL show

    MOV AH, 4CH
    INT 21H
END START
