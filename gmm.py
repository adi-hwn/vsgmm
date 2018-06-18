from sklearn.mixture import GaussianMixture
import numpy as np
import matplotlib.pyplot as plt
import os, json
from sklearn.externals import joblib # Load/Save our fitted model


DATADIR = "data/json/vs"
MODELFILE = "gmm.pkl"
NCOMPONENTS = 2
NITERS = 25000
HEROID = 9
METRICS = ['hero_damage', 'gold_per_min', 'last_hits', 'xp_per_min']


samples = []
for filename in os.listdir(DATADIR):
	match = json.load(open(DATADIR + "/" + filename,"r"))
	for player in match["players"]:
		if player["hero_id"] == HEROID:
			sample = []
			for i in range(len(METRICS)):
				sample.append(player[METRICS[i]])
			samples.append(sample)

			break


gmm = GaussianMixture(n_components=NCOMPONENTS, max_iter=NITERS, covariance_type='full')
X = np.array(samples)
gmm.fit(X)

joblib.dump(gmm, MODELFILE)