import numpy as np
import matplotlib.pyplot as plt
import os
import json

target_id = 46
target_metric = "gold_per_min"
sample_dir = "data/json/ta"

num_bins = 120

dist = []
for filename in os.listdir(sample_dir):
	match = json.load(open(sample_dir + "/" + filename,"r"))
	for player in match["players"]:
		if player["hero_id"] == target_id:
			dist.append(player[target_metric])
			#if player[target_metric] > 450:
			#	print(filename)

dist = np.array(dist)
mu, sigma = np.median(dist), np.std(dist)

# the histogram of the data
n, bins, patches = plt.hist(np.array(dist), num_bins, density=True, facecolor='y', alpha=0.75)


plt.ylabel('Proportion')
plt.xlabel(target_metric)
plt.title('Histogram')
plt.axis([max(0, mu - 3*sigma), mu + 3*sigma, 0, 300 / (mu * num_bins)])
#plt.axis([100, 600, 0, 250 / (mu * num_bins)])
plt.grid(True)
plt.show()
