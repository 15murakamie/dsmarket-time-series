# -*- coding: utf-8 -*-
"""NBEATSModel.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1W2CpRjsrY_PYqsbub1tEgM0VPS4tqAwI
"""

pip install darts

pip install dask[dataframe]

import pandas as pd
from darts import TimeSeries
from darts.models import NBEATSModel  # Modelo deep learning para séries temporais
from darts.dataprocessing.transformers import Scaler
from sklearn.preprocessing import LabelEncoder
import numpy as np
from darts.metrics import rmse
import matplotlib.pyplot as plt

dtypes = { 'id':'category',
           'item': 'category',
           'category': 'category',
           'department':'category',
           'store': 'category',
           'store_code': 'category',
           'region':'category',
           'day':'category',
           'units_sold': 'int8',
           #'date':'category',
           'weekday':'category',
           'weekday_int':'int8',
           'event':'category'}

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc1.csv', dtype=dtypes)

#  Transformando 'date' em índice temporal e ajustando variáveis categóricas
df['date'] = pd.to_datetime(df['date'])  # Garantindo que a coluna 'date' seja datetime64[ns]

# Codificando variáveis categóricas
for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

# Agrupando por data e somando 'units_sold'
df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })



df_t.head()

# Criando a série temporal para 'units_sold'
series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')

# Criando séries de covariáveis (todas as variáveis independentes)
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

# Escalando as séries para melhor treinamento
scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)
#series_covariates_scaled = scaler.fit_transform(series_covariates)

# 3. Separando os conjuntos de treino e teste
train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

# 4. Treinando o modelo com covariáveis usando N-BEATS
model = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)
                    #random_state=42)

# model = NBEATSModel(input_chunk_length=60, output_chunk_length=30, n_epochs=100)

# Treinando o modelo com as covariáveis passadas
model.fit(train_series, past_covariates=train_covariates, verbose=True)

# 5. Fazendo previsões
pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

# Revertendo a escala para os valores reais
pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

# Calcular RMSE
from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

# Salvando o modelo em formato txt
model.save()

"""Previsões por produto"""

# loaded_model = NBEATSModel.load('/content/drive/MyDrive/TFM/models/nyc1/NBEATSModel_2024-10-15_23_59_36.pt.ckpt')

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc1.csv', dtype=dtypes,index_col=False)

df_item['date'] = pd.to_datetime(df_item['date'])

sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})

# visualizando os items mais vendidos
sales = sales.sort_values(by='units_sold', ascending=False)

sales

sales_top200 = sales.head(200)

# Codificando variáveis categóricas
for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

last_date = df_item['date'].max()
last_date

# Inicializar um DataFrame vazio para armazenar todas as previsões
all_predictions = pd.DataFrame()

# Fazendo o previsão para os 200 produtos mais vendidos

#for department in departments:
#df_item = df_item[df_item['department'] == 'ACCESORIES_1']

for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions

# Loja NYC2

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc2.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'})

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.5  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

train_size2 = int(0.5  * len(series_sales_scaled))

model = NBEATSModel(input_chunk_length=90,
                    output_chunk_length=30,
                    generic_architecture = False,
                    trend_polynomial_degree = 10,
                    num_stacks= 20,
                    random_state=42,
                    n_epochs=30)




model.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)


print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()
print(f"RMSE: {rmse(test_series, pred_series)}")
# model.save()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc2.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])

sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions

# Loja NYC3

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc3.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model3 = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model3.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model3.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

model.save()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc3.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model3.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

# Loja NYC4

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc4.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model4 = NBEATSModel(input_chunk_length=720,
                    output_chunk_length=30,
                    generic_architecture = False,
                    trend_polynomial_degree = 5,
                    num_stacks= 5,
                    random_state=42,
                    n_epochs=50)

model4.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/nyc4.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model4.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions



df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos1.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model5 = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model5.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model5.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos1.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model5.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions

#BOS2

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos2.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model6 = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model6.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model6.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos2.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model6.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions

# BOS3

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos3.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model7 = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model7.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model7.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

model.save()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/bos3.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model7.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

all_predictions

#PHI1

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi1.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi1.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

# PHI2

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi2.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

model.save()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi2.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions

# PHI3

df = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi3.csv', dtype=dtypes)

df['date'] = pd.to_datetime(df['date'])

for col in ['id', 'item', 'category', 'department', 'store', 'store_code', 'region', 'weekday', 'event']:
    df[col] = LabelEncoder().fit_transform(df[col])

df_t = df.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum', })

series = TimeSeries.from_dataframe(df_t, 'date', 'units_sold')
series_covariates = TimeSeries.from_dataframe(df_t, time_col='date',
                                              value_cols=['weekday_int', 'event'])

scaler = Scaler()
series_sales_scaled = scaler.fit_transform(series)

train_size = int(0.8 * len(series_sales_scaled))
train_series = series_sales_scaled[:train_size]
test_series = series_sales_scaled[train_size:]

train_size2 = int(0.6  * len(series_sales_scaled))
train_covariates = series_covariates[:train_size]
test_covariates = series_covariates[train_size2:]

model = NBEATSModel(input_chunk_length=360,
                    output_chunk_length=30,
                    n_epochs=50)

model.fit(train_series, past_covariates=train_covariates, verbose=True)


pred_series = model.predict(n=len(test_series), past_covariates=test_covariates)

pred_series_unscaled = scaler.inverse_transform(pred_series)
test_series_unscaled = scaler.inverse_transform(test_series)

from darts.metrics import rmse
print(f"RMSE: {rmse(test_series, pred_series)}")

import matplotlib.pyplot as plt

# Plotando a série real vs. previsões
plt.figure(figsize=(10,6))
test_series_unscaled.plot(label='Real', lw=2, color='blue')
pred_series_unscaled.plot(label='Previsão', lw=2,color='red')
plt.legend()
plt.show()

model.save()

# previsões de vendas produtos

df_item = pd.read_csv('/content/drive/MyDrive/TFM/datasets/phi3.csv', dtype=dtypes,index_col=False)
df_item['date'] = pd.to_datetime(df_item['date'])
sales = df_item.groupby(['item'], as_index=False).agg({'units_sold': 'sum'})
sales = sales.sort_values(by='units_sold', ascending=False)
sales_top200 = sales.head(200)

for col in ['weekday', 'event']:
    df_item[col] = LabelEncoder().fit_transform(df_item[col])

all_predictions = pd.DataFrame()


for item in sales_top200['item']:
      # Filtrar dados por item
      df_item1 = df_item[df_item['item'] == item]

      df_item1 = df_item1.groupby(['date','event','weekday_int'], as_index=False).agg({'units_sold': 'sum'},)

      series_item = TimeSeries.from_dataframe(df_item1, 'date', 'units_sold')

      scaler = Scaler()
      series_sales_scaled = scaler.fit_transform(series_item)

      series_covariates_item = TimeSeries.from_dataframe(df_item1, time_col='date',
                                              value_cols=['weekday_int', 'event'])

      test_series_item = series_sales_scaled[train_size:]
      test_covariates_item = series_covariates_item[train_size2:]

      forecast_item = model.predict(30, series_sales_scaled, past_covariates=test_covariates_item)

      pred_series_unscaled_item = scaler.inverse_transform(forecast_item)
      test_series_unscaled_item = scaler.inverse_transform(series_sales_scaled)

      pred = pred_series_unscaled_item.pd_dataframe().T
      pred['id']=item,

      pred = pred[['id'] + [col for col in pred.columns if col != 'id']]
      all_predictions = pd.concat([all_predictions, pred], ignore_index=True)

all_predictions