import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1. Ler os dados de diversidade alfa
alpha_diversity = pd.read_csv("exported-shannon/alpha-diversity.tsv", sep="\t", header=0)
alpha_diversity.columns = ["sample-id", "shannon_entropy"]  # Renomear colunas

# 2. Ler os metadados
metadata = pd.read_csv("metadata-combined.tsv", sep="\t", header=0)

# 3. Combinar os dados de diversidade alfa com os metadados
combined_data = alpha_diversity.merge(metadata, on="sample-id")

# 4. Criar o violin plot
plt.figure(figsize=(10, 6))
sns.violinplot(
    x="condition1",  # Coluna dos metadados para agrupamento
    y="shannon_entropy",  # Coluna de diversidade alfa
    data=combined_data,
    palette="Set3",  # Esquema de cores
    cut=0,  # Ajustar a forma dos violinos
    inner="quartile",  # Mostrar quartis dentro dos violinos
)
plt.title("Diversidade Alfa (Shannon) por Condição")
plt.xlabel("Condição (condition1)")
plt.ylabel("Diversidade Alfa (Shannon)")
plt.xticks(rotation=45)  # Rotacionar rótulos do eixo x, se necessário

# 5. Salvar o gráfico em PDF
plt.tight_layout()  # Ajustar layout para evitar cortes
plt.savefig("shannon_violin_plot.pdf", format="pdf")

# 6. Mostrar o gráfico (opcional)
plt.show()
