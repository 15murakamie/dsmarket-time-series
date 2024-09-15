# elbowmethod(df_var=df_clustering, 
#             x_var='Annual Income (k$)', 
#             y_var='Spending Score (1-100)')

# Usando o Elbow Method com Elkan para definir o valor de K
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

def elbowmethod(df_var, x_var, y_var):
    X1 = df_var[[x_var, y_var]].iloc[: , :].values
    inertia = []
    for n in range(1 , 15):
        algorithm = (KMeans(n_clusters = n ,init='k-means++', n_init = 10 ,max_iter=300, 
                            tol=0.0001,  random_state= 111  , algorithm='elkan') )
        algorithm.fit(X1)
        inertia.append(algorithm.inertia_)


    plt.figure(1 , figsize = (15 ,6))
    plt.plot(np.arange(1 , 15) , inertia , 'o')
    plt.plot(np.arange(1 , 15) , inertia , '-' , alpha = 0.5)
    plt.xlabel('Number of Clusters') , plt.ylabel('Inertia')
    plt.show()

