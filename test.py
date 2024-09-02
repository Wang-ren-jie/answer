import random
import math
import test1 as t

print("終極密碼規則設定")

range1 = input("設定數字範圍，最低: ")
range2 = input("設定數字範圍，最高: ")

Fr = input("設定猜的次數: ")

if t.check(Fr) == True:
    print("Corret")
else:
    print("False")

while str.isdigit(range1) == False or str.isdigit(range2) == False or str.isdigit(Fr)== False or int(range1)>=int(range2) or int(Fr)<=0 :
    print("輸入數字範圍有誤或輸入非數字，請重新輸入: ")
    range1=input("設定數字範圍，最低: ")
    range2=input("設定數字範圍，最高: ")
    Fr=input("設定猜的次數: ")

range1=int(range1)
range2=int(range2)
Fr=int(Fr)

ansnb=int(random.randint(range1,range2))
print("終極密碼開始，範圍",range1,"~",range2)
x= input("請輸入正整數: ")
while str.isdigit(x) == False or int(x)<=range1 or int(x)>=range2 :
    x= input("輸入數字超出範圍或輸入非數字，請重新輸入: ")
while str.isdigit(x) == True :
    while Fr>1 and int(x) != ansnb:
        while str.isdigit(x) == False or int(x)<=range1 or int(x)>=range2 :
            x= input("輸入數字超出範圍或輸入非數字，請重新輸入: ")
        Fr=Fr-1
        if int(x)<ansnb:
            range1=int(x)
            print("猜錯了，還有",Fr,"次，加油!")
            print("範圍",range1,"~",range2)
            x= input("請輸入正整數: ")
            while str.isdigit(x) == False or int(x)<=range1 or int(x)>=range2 :
                x= input("輸入數字超出範圍或輸入非數字，請重新輸入: ")
        if int(x)>ansnb:
            range2=int(x)
            print("猜錯了，還有",Fr,"次，加油!")
            print("範圍",range1,"~",range2)
            x= input("請輸入正整數: ")
            while str.isdigit(x) == False or int(x)<=range1 or int(x)>=range2 :
                x= input("輸入數字超出範圍或輸入非數字，請重新輸入: ")
    if int(x)==ansnb:
        print("猜對了，遊戲結束。剩餘",Fr,"次")
        break
    else:
        print("遊戲結束，答案為:",ansnb)
        print("請再接再厲")
        break