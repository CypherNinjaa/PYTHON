import math
x=int(input("Enter the number: "))
try:
    if x<0:
        raise ValueError("-ve number not allowed")
    else:
        print("number is : ",x)
except ValueError as z:
    print(z)