with open('source.txt', 'rb') as source:
    data = source.read(10)
    with open('notex.txt', 'wb') as notex:
        notex.write(data)