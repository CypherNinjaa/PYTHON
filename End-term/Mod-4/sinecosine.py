import numpy as np
import matplotlib.pyplot as plt

# Generate x values
x = np.linspace(0, 2*np.pi, 100)

# Compute sine and cosine
y1 = np.sin(x)
y2 = np.cos(x)

# Plot graphs
plt.plot(x, y1, label="Sine Curve")
plt.plot(x, y2, label="Cosine Curve")

# Labels and title
plt.xlabel("Angle (radians)")
plt.ylabel("Value")
plt.title("Sine and Cosine Curves")

# Show legend
plt.legend()

# Display graph
plt.show()