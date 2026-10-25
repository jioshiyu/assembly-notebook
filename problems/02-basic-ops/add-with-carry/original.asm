; ===== 原始作业源码（照抄，MASM 语法，仅存档对照，不参与编译）=====
.MODEL SMALL
.STACK 100
.DATA
.CODE 
START:
    MOV AL,93H
    MOV BL,78H
    ADD AL,BL   
    MOV DL,AL
    MOV DH,0
    ADC DH,0
    
    
END START
