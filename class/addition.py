class Addition:
    
    def add(self):
        self.a = int(input("enter the 1st number: "))
        self.b = int(input("enter the 2nd number: "))
    
    def display(self):
       print("sum",self.a + self.b)

calc = Addition()

calc.add()
calc.display()