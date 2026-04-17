filename = input("enter the file name: ")
with open(filename) as file:
    text = file.read()
letter = input("Enter the character : ")
count=0
for char in text:
    if char == letter:
        count+=1
print(letter,"appear",count,"times in file")