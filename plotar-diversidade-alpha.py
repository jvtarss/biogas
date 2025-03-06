import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

alpha_diversity = pd.read_csv("exported-shannon/alpha-diversity.tsv", sep="\t", header=0)
alpha_diversity.columns = ["sample-id", "shannon_entropy"]  # renomear colunas

metadata = pd.read_csv("metadata-combined.tsv", sep="\t", header=0)

combined_data = alpha_diversity.merge(metadata, on="sample-id")

plt.figure(figsize=(10, 6))
sns.violinplot(
    x="condition1",  # coluna dos metadados para agrupamento
    y="shannon_entropy",  # coluna de diversidade alfa
    data=combined_data,
    palette="set3",  # esquema de cores
    cut=0,  # ajustar a forma dos violinos
    inner="quartile",  # mostrar quartis dentro dos violinos
)
plt.title("diversidade alfa (shannon) por condicao")
plt.xlabel("condicao (condition1)")
plt.ylabel("diversidade alfa (shannon)")
plt.xticks(rotation=45)  # rotacionar rotulos do eixo x, se necessario

plt.tight_layout()  # ajustar layout para evitar cortes
plt.savefig("shannon_violin_plot.pdf", format="pdf")

plt.show()
