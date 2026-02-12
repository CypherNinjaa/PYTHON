#1st condition: if it is divisible by 4 but not by 100
#2nd condition: or it is divsible by 400 
num =int(input("Enter the year: "))
if  (num%4==0 and num%100!=0) or(num%400 ==0):
    print(num," is a leap year")
else:
    print("it is not a leap year")