import csv
try:
    with open("csvfile.csv","a",newline="") as f:
        writer=csv.writer(f)
        writer.writerow(["vikash",100])
except FileNotFoundError:
    print("file not found")