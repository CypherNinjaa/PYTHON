# sum of series: (1+1/2**2.....+1/n**2)
num = int(input("Enter the number: "))
sum =0
for i in range(1,num+1):
    sum = sum+1/(i**2)
print("sum of series: ",sum)