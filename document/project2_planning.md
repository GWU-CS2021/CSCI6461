# Requirements
Implement all instructions except for

CHK
Floating Point/Vector operations
Trap
program1
backend

instruction

# Backend/Panel @ ruojia
- instructions
  - jump
  - add/multiply
  - rotation
  - IN/OUT?
- return in another single for in command(waiting for input)
- cache/memory

- frontend
- virtual keyboard
- cache monitor
- virtual output textbox

# compiler/assembler @ guanyu
  - ld/store
  - jump
  - add/multiply
  - rotation
  - IN/OUT?
generate IPL.txt

# asm file @ zhengyi
## program 1:

Program 1: A program that reads 20 numbers (integers) from the keyboard, prints the numbers to the console printer, 
requests a number from the user, and searches the 20 numbers read in for the number closest to the number entered by 
the user. Print the number entered by the user and the number closest to that number. Your numbers should not be 1…10, 
but distributed over the range of 0 … 65,535. Therefore, as you read a character in, you need to check it is a digit, 
convert it to a number, and assemble the integer.


## use IN command to input
pesudo code
```python
for reg0 in 1-21:
  for input not [enter]:
    wait for keyboard input into reg1 (IN command)
    output the charactor if valid/ignore if invalid
    convert single char to int(ascii 48--57 -> 0-9) (add command)
    multiply target reg(reg2) by 10(mul command)
    add current int from temp register(reg1) into target register(reg2)
  save register(reg2) into memory after user hit enter(ascii 13)
for reg0 in 1-20:
  reg2 memory compare
  save current difference into reg1
  reg2 - currentmemory [reg0] -> reg3（abs)
  if reg3< reg1
    reg1 = reg3
  currentmemory [reg0] -> memory[min_adrr]
memory[min_adrr] -> reg0
out reg0
```
# test cases @ Alan
Create test cases for cpu backend
https://github.com/GWU-CS2021/CSCI6461/blob/d8e9e718ceda1e962158d5c3d7856817ef862a3a/project/src/cpu.py#L170
