with open("table.txt", "w", newline="") as f:
    for i in range(1, 11):
        result = i * 2
        f.write(str(result) + "\n")
