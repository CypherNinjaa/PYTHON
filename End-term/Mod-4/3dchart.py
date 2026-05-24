import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

x = [1, 2, 3]
y = [4, 5, 6]
z = [7, 8, 9]

ax.plot(x, y, z)
plt.show()