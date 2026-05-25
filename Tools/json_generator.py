import os
import json

data = [[],[],[],[],[]]

data[0] = ["prout", "caca", "pipi"]
data[1] = [1,2,3,4,5,6,7,8,9,10]
data[2] = [1,2,3,4,5,6,7,8,9,10]
data[3] = [10,9,8,7,6,5,4,3,2,1]
data[4] = [1,2,1,2,1,2,1,2,1,2]


with open("log.json", "a") as f :
    json.dump(data, f)