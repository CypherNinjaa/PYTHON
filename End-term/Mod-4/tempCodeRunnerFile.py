# JSON reading
with open("file.json", "r") as f:
    data = json.load(f)
    print(data)