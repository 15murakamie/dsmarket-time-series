# scatter_plot2D(df_var=df_price, 
#                x_var='yearweek', 
#                y_var='sell_price', 
#                x_label='Período', 
#                y_label='Preço de Venda')

import matplotlib.pyplot as plt

# Scatter plot baseado em 2 variáveis
def scatter_plot2D(df_var, x_var, y_var, x_label, y_label):
    plt.figure(1 , figsize = (15 , 7))
    plt.title(f'Scatter plot of {x_label} x {y_label}', fontsize = 20)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.scatter(df_var[x_var], df_var[y_var], s = 100)
    plt.show()

