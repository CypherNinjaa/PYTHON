s1 = "Hello"
s2 = "world"
#1. length
print("length of s1",len(s1))
# 5. Concatenation
print(s1+s2)

# 2. Upper & Lower
print("Upper: ",s1.upper())
print("lower: ",s1.lower())
s3 = """hello
world
hello 
world"""
#3. indexing
print(s3[1])

#4. slicing
print("slice (0:5)",s3[0:7])

# 6. Repetition
print("Repetition:", s1 * 2)


# 7. Membership
print("hello" in s3)

#8. replace
print(s3.replace("world","vikash"))

#9. join
words = ["hello ", "vikash"]
print("".join(words))

#10. split
print("Split:", s3.split())

#11. strip
print(s3.strip())

#12. find
s5 = " world hello"
print(s5.find("hello"))

#13. count
s6 = "hello"
print(s6.count("l"))
s4 = "hey! vikash"
s4 = "H"+ s4[1:]
print(s4[1:4])
del s4[1]
for char in s4:
    print(char)