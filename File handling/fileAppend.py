file = open("note.txt", "a")
file.writelines(input("enter your name: "))
file.close()
print("data written into file......")