import pandas as pd
import numpy as np
from sklearn import manifold
from sklearn.metrics import euclidean_distances
import matplotlib.pyplot as plt

pd.set_option('display.width', 500)

seed = np.random.RandomState(seed=3)
df = pd.DataFrame(pd.read_csv('/Users/JackShipway/Downloads/bq.csv',
                              usecols=['Visitors', 'Reports', 'TimeSpent'])).fillna(0)

for i in df.columns:
    df[i] = (df[i] - np.mean(df[i])) / np.std(df[i])

sim = euclidean_distances(df)

mds = manifold.MDS(n_components=2, max_iter=3000, eps=1e-9,
                   random_state=seed, dissimilarity="precomputed", n_jobs=1)

pos = mds.fit(sim).embedding_

plt.plot(pos[0,:], pos[1,:])
plt.show()
