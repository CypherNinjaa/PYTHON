file = open("note.txt", "w")
file.writelines(input("enter your name: "))
file.close()
print("data written into file......")