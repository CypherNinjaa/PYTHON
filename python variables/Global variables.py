# Variables that are created outside of a function (as in all of the examples in the previous pages) are known as global variables.

# Global variables can be used by everyone, both inside of functions and outside.

x = " awesome"
def myfunc():
    print("python is" + x)

myfunc()

# If you create a variable with the same name inside a function, this variable will be local, and can only be used inside the function. The global variable with the same name will remain as it was, global and with the original value.

x = "awesome"
def myfunc():
    x = "fantastic"
    print("pyton is "+x)
myfunc()

print ("python is " + x)

# The global Keyword
# Normally, when you create a variable inside a function, that variable is local, and can only be used inside that function.

# To create a global variable inside a function, you can use the global keyword.
def myfunction():
    global y;
    y = "fantastic2"
myfunction()

print("python is "+ y)

# Also, use the global keyword if you want to change a global variable inside a function.

z = "i am global"
def myfunction():
    global z
    z = "i am changed using global keyword"
myfunction()
print(z)