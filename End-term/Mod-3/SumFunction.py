import sys
def sum(a, b):
    print(a+b)
# x = int(input("Enter first number: "))
# y = int(input("Enter second number: "))
sum(sys.argv[1],sys.argv[2])

print(sys.argv[0])