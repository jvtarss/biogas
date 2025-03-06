import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import randomforestregressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

dados = pd.read_csv("phyla_abundance_by_condition-phyla.csv")

print(dados.head())

x = dados.drop(columns=['condition1'])
y = dados['condition1']

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)

modelo_rf = randomforestregressor(n_estimators=100, random_state=42)

modelo_rf.fit(x_train, y_train)

y_pred = modelo_rf.predict(x_test)

mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"erro quadratico medio (mse): {mse:.4f}")
print(f"r-quadrado: {r2:.4f}")

importancia = modelo_rf.feature_importances_
variaveis = x.columns

importancia_df = pd.dataframe({'variavel': variaveis, 'importancia': importancia})
importancia_df = importancia_df.sort_values(by='importancia', ascending=false)

plt.figure(figsize=(12, 6))
sns.barplot(x='importancia', y='variavel', data=importancia_df.head(10))
plt.title('importancia das variaveis no modelo random forest')
plt.xlabel('importancia')
plt.ylabel('variavel')
plt.show()

plt.figure(figsize=(8, 8))
plt.scatter(y_test, y_pred)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
plt.xlabel('valores reais')
plt.ylabel('previsoes')
plt.title('previsoes vs valores reais')
plt.show()
