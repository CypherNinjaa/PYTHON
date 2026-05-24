try:
    with open("binary.txt","rb") as f:
        x = f.read()
        print(x)
except FileNotFoundError:
    print("file not found")