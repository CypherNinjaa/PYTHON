import csv
with open("csvfile.csv","w",newline="")as f:
    writer = csv.writer(f)
    writer.writerow(["name","marks"])
    writer.writerow(["vikash",90])
    writer.writerow(["rahul",90])
