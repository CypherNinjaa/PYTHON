import csv
with open("csvfile.csv")as f:
    reader = csv.reader(f)
    for row in reader:
        print(row)