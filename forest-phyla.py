# Importar bibliotecas necessárias
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

# Carregar os dados do arquivo CSV
dados = pd.read_csv("phyla_abundance_by_condition-phyla.csv")

# Exibir as primeiras linhas do DataFrame para verificar os dados
print(dados.head())

# Remover a coluna de condições, que não será utilizada como preditora
X = dados.drop(columns=['condition1'])
y = dados['condition1']

# Dividir os dados em conjuntos de treinamento e teste (70% treino, 30% teste)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Criar o modelo Random Forest
modelo_rf = RandomForestRegressor(n_estimators=100, random_state=42)

# Treinar o modelo
modelo_rf.fit(X_train, y_train)

# Fazer previsões no conjunto de teste
y_pred = modelo_rf.predict(X_test)

# Avaliar o desempenho do modelo
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Erro Quadrático Médio (MSE): {mse:.4f}")
print(f"R-quadrado: {r2:.4f}")

# Avaliar a importância das variáveis
importancia = modelo_rf.feature_importances_
variaveis = X.columns

# Criar um DataFrame para visualizar a importância das variáveis
importancia_df = pd.DataFrame({'Variável': variaveis, 'Importância': importancia})
importancia_df = importancia_df.sort_values(by='Importância', ascending=False)

# Plotar a importância das variáveis
plt.figure(figsize=(12, 6))
sns.barplot(x='Importância', y='Variável', data=importancia_df.head(10))
plt.title('Importância das Variáveis no Modelo Random Forest')
plt.xlabel('Importância')
plt.ylabel('Variável')
plt.show()

# Visualizar previsões vs valores reais
plt.figure(figsize=(8, 8))
plt.scatter(y_test, y_pred)
plt.plot([y.min(), y.max()], [y.min(), y.max()], 'k--', lw=2)
plt.xlabel('Valores Reais')
plt.ylabel('Previsões')
plt.title('Previsões vs Valores Reais')
plt.show()
