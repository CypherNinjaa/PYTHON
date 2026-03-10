arith = int(input("enter the number: 1 for ad, 2 for sub, 3 for multiply, 4 for division: "))
x = int(input("enter the first number: "))
y =int(input("enter the 2nd number: "))

match arith:
    case 1:
        print("sum:",x+y)
    case 2:
        print("Subtract:",x-y)
    case 3:
        print("multiplied:",x*y)
    case 4:
        if x>0:
            print("can't divide by zero")
        else:
            print("divided: ",x/y)
    case _:
        print("enter the valid option and number")



