import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from skbio.stats.ordination import OrdinationResults

# 1. Ler os dados do PCoA e verificar a estrutura
pcoa_results = OrdinationResults.read("exported-pcoa/ordination.txt")
print("Shape of PCoA samples:", pcoa_results.samples.shape)
print("PCoA columns:", pcoa_results.samples.columns)

# 2. Converter os dados do PCoA para DataFrame e renomear colunas apropriadamente
pcoa_df = pd.DataFrame(
    pcoa_results.samples.values,
    index=pcoa_results.samples.index,
    columns=[f"PC{i+1}" for i in range(pcoa_results.samples.shape[1])]
)

# Verificar a estrutura após a conversão
print("\nPCoA DataFrame columns after conversion:", pcoa_df.columns)

# 3. Adicionar o sample-id como coluna
pcoa_df = pcoa_df.reset_index()
pcoa_df = pcoa_df.rename(columns={'index': 'sample-id'})

# 4. Ler os metadados
metadata = pd.read_csv("metadata-combined.tsv", sep="\t")

# 5. Combinar os dados do PCoA com os metadados
merged_df = pcoa_df.merge(metadata, on="sample-id")
print("\nMerged DataFrame columns:", merged_df.columns)

# Verificar os grupos únicos em 'condition1'
unique_conditions = merged_df['condition1'].unique()
print("Unique conditions in 'condition1':", unique_conditions)

# 6. Criar o gráfico PCoA com elipses, cores e formas diferentes para cada grupo

# Definir a paleta de cores 'rainbow'
palette = sns.color_palette("rainbow", n_colors=len(unique_conditions))

# Definir formas diferentes para cada grupo (uma forma para cada condição)
markers = ['o', 's', 'D', '^', 'v', '<', '>', 'P', '*', 'X']  # Lista de formas disponíveis
marker_dict = {condition: markers[i % len(markers)] for i, condition in enumerate(unique_conditions)}

plt.figure(figsize=(10, 8))
sns.set_style("whitegrid")

# Scatter plot dos pontos do PCoA com diferentes formas e cores
for condition in unique_conditions:
    subset = merged_df[merged_df['condition1'] == condition]
    plt.scatter(
        subset['PC1'],
        subset['PC2'],
        label=condition,
        color=palette[list(unique_conditions).index(condition)],
        marker=marker_dict[condition],  # Usar forma específica para cada grupo
        s=100  # Tamanho dos pontos
    )

# Adicionar elipses de confiança
sns.kdeplot(
    data=merged_df,
    x="PC1",
    y="PC2",
    hue="condition1",
    levels=5,
    thresh=0.2,
    palette=palette,
    alpha=0.3
)

# Ajustar o layout do gráfico PCoA
plt.title("PCoA Bray-Curtis (Hellinger) com Elipses de Agrupamento")
plt.xlabel(f"PC1 ({pcoa_results.proportion_explained[0]*100:.2f}%)")
plt.ylabel(f"PC2 ({pcoa_results.proportion_explained[1]*100:.2f}%)")
plt.legend(title="Condition1", bbox_to_anchor=(1.05, 1), loc="upper left")

# Salvar o gráfico PCoA em PDF
plt.tight_layout()
plt.savefig("pcoa_bray_curtis_hellinger_elipses.pdf", format="pdf", bbox_inches="tight")
plt.show()

# 7. Criar o gráfico de violino com base na diversidade alfa

# Ler os dados de diversidade alfa (Shannon)
alpha_diversity = pd.read_csv("exported-shannon/alpha-diversity.tsv", sep="\t", header=0)
alpha_diversity.columns = ["sample-id", "shannon_entropy"]  # Renomear colunas

# Combinar os dados de diversidade alfa com os metadados
combined_data = alpha_diversity.merge(metadata, on="sample-id")

# Criar o gráfico de violino usando a mesma paleta de cores do PCoA
plt.figure(figsize=(10, 6))
sns.violinplot(
    x="condition1",  # Coluna dos metadados para agrupamento
    y="shannon_entropy",  # Coluna de diversidade alfa
    data=combined_data,
    palette=palette,  # Usar a mesma paleta de cores do PCoA
    cut=0,  # Ajustar a forma dos violinos (não extrapolar os dados)
    inner="quartile"  # Mostrar quartis dentro dos violinos
)

# Ajustar o layout do gráfico de violino
plt.title("Diversidade Alfa (Shannon) por Condição")
plt.xlabel("Condição (condition1)")
plt.ylabel("Diversidade Alfa (Shannon)")
plt.xticks(rotation=45)  # Rotacionar rótulos do eixo x, se necessário

# Salvar o gráfico de violino em PDF
plt.tight_layout()
plt.savefig("shannon_violin_plot.pdf", format="pdf")

# Mostrar o gráfico de violino (opcional)
plt.show()
