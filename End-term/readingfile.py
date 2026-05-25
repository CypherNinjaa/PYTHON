with open("table.txt","a") as f:
    for i in range(1,11):
        sum = 4*i
        f.write(str(sum)+"\n")

with open("table.txt","r")as f:
    t=f.read()
    print(t)