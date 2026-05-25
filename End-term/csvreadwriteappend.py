import csv
# try:
#     with open("csvfile.csv","w",newline="")as f:
#         writer = csv.writer(f)
#         writer.writerow(["name","age"])
#         writer.writerow(["vikash","24"])
# except:
#     print("something went wrong")

try:
    with open("csvfile.csv")as f:
        # raise FileNotFoundError
        reader=csv.reader(f)
        for row in reader:
            print(row)

except FileNotFoundError:
    print("file not found")
        
