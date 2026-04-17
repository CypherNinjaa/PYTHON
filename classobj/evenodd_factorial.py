# Parent class
class evenodd:
    def Evenodd(self, a):
        if a % 2 == 0:
            print("It is an even number")
        else:
            print("It is an odd number")
            
# Child class
class fact(evenodd):
    def factorial(self, n):
        fact = 1
        for i in range(1, n + 1):
            fact *= i
        print("Factorial is:", fact)

obj = fact()
a = int(input("Enter the number: "))
obj.Evenodd(a)
obj.factorial(a)