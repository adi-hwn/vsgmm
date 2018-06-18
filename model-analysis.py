from sklearn.mixture import GaussianMixture
import numpy as np
import matplotlib.pyplot as plt
import os, json
from sklearn.externals import joblib # Load/Save our fitted model
from scipy.stats import multivariate_normal

DATADIR = "data/json/vs"
MODELFILE = "gmm.pkl"
COMPONENT_COLORS = ['y', 'r', 'g', 'tab:purple', 'k']
COMPONENT_COLORMAPS = ['Reds', 'Blues', 'Greens', 'Purples', 'Blacks']
HEROID = 20
METRICS = ['hero_damage', 'gold_per_min', 'last_hits', 'xp_per_min']
PLOTMETRICS = ['last_hits', 'gold_per_min']
PLOTMETRICIDXS = [2, 1]
ITEM_KEYS = ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5', 'backpack_0', 'backpack_1', 'backpack_2']
NITEMS_DISPLAYED = 40
SIDE_SLOT_MASK = 0x80
GRIDX = 50
GRIDY = 50

ItemDict = json.load(open("parsing/items.json"))
ItemIDs = dict(zip(ItemDict.keys(), range(len(ItemDict.keys()))))
#print(ItemIDs)

samples = []
points = [[], []]
playeritems = []
playerwins = []
for filename in os.listdir(DATADIR):
	match = json.load(open(DATADIR + "/" + filename,"r"))
	for player in match["players"]:
		if player["hero_id"] == HEROID:
			sample = []
			for i in range(len(METRICS)):
				sample.append(player[METRICS[i]])
			samples.append(sample)

			points[0].append(player[PLOTMETRICS[0]])
			points[1].append(player[PLOTMETRICS[1]])

			player_is_dire = (player["player_slot"] & SIDE_SLOT_MASK) != 0
			radiant_wins = match["radiant_win"]
			if player_is_dire != radiant_wins:
				playerwins.append(1)
			else:
				playerwins.append(0)

			itemvec = [0] * len(ItemIDs)
			for key in ITEM_KEYS:
				if key in player:
					item_id = str(player[key])
					if item_id in ItemDict:
						#print(match["match_id"], ItemDict[item_id]["localized_name"])
						itemvec[ItemIDs[item_id]] = 1

			playeritems.append(itemvec)

			break

playerwins = np.array(playerwins)
playeritems = np.array(playeritems)
X = np.array(samples)
n_samples = X.shape[0]

gmm = joblib.load(MODELFILE)
n_components = gmm.weights_.shape[0]
labeled_points = []
labels = gmm.predict(X)
labels_onehot = np.zeros((len(labels), n_components))
for i in range(n_components):
	labeled_points.append([[], []])
for i in range(len(labels)):
	labeled_points[labels[i]][0].append(points[0][i])
	labeled_points[labels[i]][1].append(points[1][i])

	labels_onehot[i,labels[i]] = 1


print("%(c)d samples, Overall winrate: %(w).4f%%" % {"c": len(samples), "w": 100*np.sum(playerwins) / n_samples})
print("Most built items (Overall):")
itemRates = []
for item in ItemIDs:
	total = np.sum(playeritems[:,ItemIDs[item]])
	wins = np.sum(playeritems[:,ItemIDs[item]] * playerwins)
	winrate = 0
	if total > 0:
		winrate = wins / total
	itemRates.append((total / n_samples, item, winrate))
itemRates.sort(reverse=True)
for i in range(min(len(itemRates), NITEMS_DISPLAYED)):
	rate, item, wins = itemRates[i]
	print("{0:25}: buildrate {1:.4f}%, winrate {2:.4f}%".format(ItemDict[item]["localized_name"], rate*100, wins*100))

print("\n")

for j in range(n_components):
	cluster_pop = np.sum(labels_onehot[:,j])
	if cluster_pop > 0:
		print("Cluster", j, "%(c)d/%(t)d samples (%(p).4f%%)" % {"c": cluster_pop, "t": n_samples, "p": 100*cluster_pop/n_samples})
		print("Winrate: %(w).4f%%" % {"w": 100*np.sum(labels_onehot[:,j] * playerwins) / cluster_pop})
		print("Metric stats (mean, stdev):")
		for i in range(len(METRICS)):
			print(METRICS[i],":(", gmm.means_[j,i],",", np.sqrt(gmm.covariances_[j,i,i]),")")

		print("\nMost popular items:")
		itemRates = []
		for item in ItemIDs:
			total = np.sum(playeritems[:,ItemIDs[item]] * labels_onehot[:, j])
			wins = np.sum(playeritems[:,ItemIDs[item]] * labels_onehot[:, j] * playerwins)
			winrate = 0
			if total > 0:
				winrate = wins / total
			itemRates.append((total / cluster_pop, item, winrate))
		itemRates.sort(reverse=True)
		for i in range(min(len(itemRates), NITEMS_DISPLAYED)):
			rate, item, wins = itemRates[i]
			print("{0:25}: buildrate {1:.4f}%, winrate {2:.4f}%".format(ItemDict[item]["localized_name"], rate*100, wins*100))
		print("\n")


mu, sigma = np.mean(points, axis=1), np.std(points, axis=1)
plt.xlabel(PLOTMETRICS[0])
plt.ylabel(PLOTMETRICS[1])
plt.title('Scatterplot')

plt_minx = max(0, mu[0] - 4*sigma[0])
plt_maxx = mu[0] + 4*sigma[0]
plt_miny = max(0, mu[1] - 4*sigma[1])
plt_maxy = mu[1] + 4*sigma[1]

plt.axis([plt_minx, plt_maxx, plt_miny, plt_maxy])
#plt.axis([100, 600, 0, 250 / (mu * num_bins)])

x = np.linspace(plt_minx, plt_maxx, GRIDX)
y = np.linspace(plt_miny, plt_maxy, GRIDY)
X, Y = np.meshgrid(x, y)
XY = np.stack((X, Y), axis=2)

for i in range(n_components):
	p0, p1 = PLOTMETRICIDXS[0], PLOTMETRICIDXS[1]
	Zm = np.array([gmm.means_[i,p0], gmm.means_[i,p1]])
	Zcov = np.array([[gmm.covariances_[i,p0,p0], gmm.covariances_[i,p0,p1]], [gmm.covariances_[i,p1,p0], gmm.covariances_[i,p1,p1]]])
	Z = multivariate_normal(mean=Zm, cov=Zcov)
	#plt.contourf(X, Y, Z.pdf(XY), 10, cmap=COMPONENT_COLORMAPS[i], alpha=1/(i+1))
	plt.scatter(labeled_points[i][0], labeled_points[i][1], c=COMPONENT_COLORS[i])
plt.show()