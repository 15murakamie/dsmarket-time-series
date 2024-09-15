# agglomerative_clust(df_var=df_clustering, 
#                    x_var='Annual Income (k$)', 
#                    y_var='Spending Score (1-100)',
#                    nclust=5)

# Fazendo clustering com N=5
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering

def agglomerative_clust(df_var, x_var, y_var, nclust):
    X1 = df_var[[x_var, y_var]].iloc[: , :].values
    hc = AgglomerativeClustering(n_clusters = nclust, metric = 'euclidean', linkage = 'ward')
    y_hc = hc.fit_predict(X1)
    
    # Plot dos Clusters
    for i in range (nclust):
        plt.scatter(X1[y_hc == i, 0], X1[y_hc == i, 1], s = 100)
    plt.title('Clusters of customers')
    plt.xlabel(x_var)
    plt.ylabel(y_var)
    plt.legend()
    plt.show()