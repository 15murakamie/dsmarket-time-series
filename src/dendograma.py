# dendograma(df_clustering, 
#             'Annual Income (k$)', 
#             'Spending Score (1-100)')

# Fazendo dendograma
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import linkage, dendrogram

def dendograma(df_var, x_var, y_var):
    X1 = df_var[[x_var, y_var]].iloc[: , :].values
    Z = linkage(X1, 'ward')
    plt.figure(figsize=(40, 25))
    plt.title('Hierarchical Clustering Dendrogram')
    plt.xlabel(x_var + 'x' + y_var)
    plt.ylabel('distance')
    dendrogram(
        Z,
        leaf_rotation=90.,
        leaf_font_size=8.,
    )
    plt.show()

