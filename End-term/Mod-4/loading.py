import pickle
with open("picklefile.dat","rb") as f:
    x=pickle.load(f)
    print(x)