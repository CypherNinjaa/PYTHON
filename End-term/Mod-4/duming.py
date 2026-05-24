import pickle
data = [1,2,3,4]
with open("picklefile.dat","wb") as f:
    pickle.dump(data,f)
    