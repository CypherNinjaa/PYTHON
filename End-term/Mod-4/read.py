try:
    with open("test.txt","r") as f:
        x=f.read()
        print(len(x))
except FileNotFoundError:
    print("Error: The file 'test.txt' does not exist. Please check the file path and try again.")