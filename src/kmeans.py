# kmeans_clust(df_clustering, 
#             'Annual Income (k$)', 
#             'Spending Score (1-100)',
#             5)

# Fazendo clustering com N=5
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def kmeans_clust(df_var, x_var, y_var, nclust):
    X1 = df_var[[x_var, y_var]].iloc[: , :].values

    algorithm = (KMeans(n_clusters = nclust ,init='k-means++', n_init = 10 ,max_iter=300, 
                            tol=0.0001,  random_state= 111  , algorithm='elkan') )
    algorithm.fit(X1)
    labels1 = algorithm.labels_
    centroids1 = algorithm.cluster_centers_

    h = 0.02
    x_min, x_max = X1[:, 0].min() - 1, X1[:, 0].max() + 1
    y_min, y_max = X1[:, 1].min() - 1, X1[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    Z = algorithm.predict(np.c_[xx.ravel(), yy.ravel()]) 

    plt.figure(1 , figsize = (15 , 7) )
    plt.clf()
    Z = Z.reshape(xx.shape)
    plt.imshow(Z , interpolation='nearest', 
            extent=(xx.min(), xx.max(), yy.min(), yy.max()),
            cmap = plt.cm.Pastel2, aspect = 'auto', origin='lower')
    plt.title('Clusters of customers')
    plt.scatter( x = x_var, y = y_var, data = df_var, c = labels1, s = 100)
    plt.scatter(x = centroids1[: , 0] , y =  centroids1[: , 1] , s = 300 , c = 'red' , alpha = 0.5)
    plt.ylabel(x_var) , plt.xlabel(y_var)
    plt.show()

