try:
    x = int(input("Enter number: "))
    result = 10 / x
except:
    print("an error occured")
# else:
    # print(int(result))
finally:
    print("code executed")