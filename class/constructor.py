class ABC():
    def __init__(self,val):
        print("Inclass Method......")
        self.val=val
        print("the value is:",val)
obj = ABC(14)