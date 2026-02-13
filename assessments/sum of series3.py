# question: 1/2 + 2/3..........+n/(n+1)
num = int(input("Enter the Number: "))
sum=0
for i in range(1,num+1):
    sum+=i/(i+1)
print("Sum of series: ",sum)