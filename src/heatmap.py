# heatmap(df_var=df_remove_0, 
#         x_var='department', 
#         y_var='store_code',
#         target='units_sold',
#         agg='sum')

import seaborn as sns
import matplotlib.pyplot as plt

def heatmap(df_var, x_var, y_var, target, agg):
    # Pivotando o dataframe
    heatmap_data = df_var.pivot_table(index=y_var, columns=x_var, values=target, aggfunc={agg})

    # Criando o heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': {target}})
    plt.xlabel(x_var)
    plt.ylabel(y_var)
    plt.title(f'Mapa de calor de {x_var} x {y_var}', fontsize = 20)
    plt.show()