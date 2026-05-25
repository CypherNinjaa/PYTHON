with open("binary.txt","wb")as f:
    f.write(b"101010")

with open("binary.txt","rb")as f:
    x=f.read()
    print(x)
    