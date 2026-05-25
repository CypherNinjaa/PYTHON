try:
    with open("csvfile.csv")as f:
        # raise FileNotFoundError
        reader=reader.csv(f)
        for row in reader:
            print(row)

except FileNotFoundError:
    print("file not found")