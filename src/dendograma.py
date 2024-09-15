# dendograma(df_var=df_sold_week_x_depart, 
#                     x_var='units_sold', 
#                     y_var='sell_price')


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

