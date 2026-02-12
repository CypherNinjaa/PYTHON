num = int(input("enter the numbner: "))
num2 = num #store value to compare
temp = num #temp variable to count digits
n = 0 #count the digit
result =0 #store pow
remainder = 0 #store remainder

# count the number of digit
while temp!=0:
    temp //= 10
    n = n+1

# calculate the armstrong
for i in range(n):
    remainder = num2%10
    result += pow(remainder,n)
    num2 //=10

#compare the reusult and the num
if result ==num:
    print(num," is an armstrong number")
else:
    print("it is not an armstrong")

