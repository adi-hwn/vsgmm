import numpy as np
import matplotlib.pyplot as plt
import os
import json

target_id = 20
target_metricx = "gold_per_min"
target_metricy = "last_hits"
sample_dir = "data/json/vs"

distx = []
disty = []
for filename in os.listdir(sample_dir):
	match = json.load(open(sample_dir + "/" + filename,"r"))
	for player in match["players"]:
		if player["hero_id"] == target_id:
			distx.append(player[target_metricx])
			disty.append(player[target_metricy])
			#if player[target_metric] > 450:
			#	print(filename)

print(len(distx))
print(len(os.listdir(sample_dir)))

distx = np.array(distx)
mux, sigmax = np.median(distx), np.std(distx)
disty = np.array(disty)
muy, sigmay = np.median(disty), np.std(disty)


plt.ylabel(target_metricy)
plt.xlabel(target_metricx)
plt.title('Scatterplot')
plt.axis([max(0, mux - 4*sigmax), mux + 4*sigmax, max(0, muy - 4*sigmay), muy + 4*sigmay])
#plt.axis([100, 600, 0, 250 / (mu * num_bins)])
plt.scatter(distx, disty, c='r')
plt.show()
