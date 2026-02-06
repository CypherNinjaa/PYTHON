a = float(input("enter the 1st side of traingle: "))
b = float(input("enter the 2nd side of traingle: "))
c = float(input("enter the 3rd side of traingle: "))
# calculating s 
s = (a+b+c)/2
area = (s*(s-a)*(s-b)*(s-c))**0.5
print("area of traingle: ",area)