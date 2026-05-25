import os
import json
import matplotlib.pyplot as plt
import numpy as np

data = 0
with open("log.json", "r") as f :
    data = json.load(f)

for i in range(2, len(data)):
    plt.plot(data[1], data[i], label = data[0][i-2])

plt.xlabel("Temps(s)")
plt.title("Log robot")
plt.legend()
plt.show()
