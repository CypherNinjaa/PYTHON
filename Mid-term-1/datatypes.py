# numeric 
a = 10;
b = 4.4
c = 4+4j

print(type(a))
print(type(b))
print(type(c))

# sequence type
# string
s = "welcoem to the geeks world"

print (type(s))
print(s[0])
print(s[-1])

# list
a = [1,2,3,4]
b = [20,10]
a.append(100)
a.insert(2,200)
a.extend([10,20,30])
print(a+b)
print(a[-1])


# tuples
tup1 = (1, 2, 3, 4, 5)
tup2 = (1, 2, 3, 4, 5)
print(tup1+tup2)
# access tuple items
print(tup1[0])
print(tup1[-1])
print(tup1[-3])

# set
s1 = set()
s1 = set("helloworld")
print("set with the use of string : ",s1)

# dictionary
d = {}
d = {1:'geeks',2:'for',3:'geeks'}
print(d)
print(d.get(1))
print(d[2])