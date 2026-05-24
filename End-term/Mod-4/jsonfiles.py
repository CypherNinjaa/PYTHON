import csv
import json

# JSON writing
data = {"name": "vikash", "marks": 88}
with open("file.json", "w") as f:
    json.dump(data, f)

# JSON reading
with open("file.json", "r") as f:
    data = json.load(f)
    print(data)