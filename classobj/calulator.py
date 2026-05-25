#parent class
class calculator:
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def add(self):
        print("Addition =", self.a + self.b)
    def sub(self):
        print("Subtraction =", self.a - self.b)
    def multiply(self):
        print("Multiplication =", self.a * self.b)
    def divide(self):
        if self.b != 0:
            print("Division =", self.a / self.b)
        else:
            print("Division by zero is not allowed")

num = float(input("Enter first number: "))
num2 = float(input("Enter second number: "))
calc = calculator(num, num2)
print("Enter the specific value: ")
print("1. Add, 2. Sub, 3. Multiply, 4. Divide")
arith = int(input("Enter your choice: "))
match arith:
    case 1:
        calc.add()
    case 2:
        calc.sub()
    case 3:
        calc.multiply()
    case 4:
        calc.divide()
    case _:
        print("enter the valid option and number") 