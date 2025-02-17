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

# 5. Combinar os dados
merged_df = pcoa_df.merge(metadata, on="sample-id")
print("\nMerged DataFrame columns:", merged_df.columns)

# Verificar os grupos únicos em 'condition1'
unique_conditions = merged_df['condition1'].unique()
print("Unique conditions in 'condition1':", unique_conditions)

# 6. Criar o gráfico PCoA com elipses e formas diferentes para cada grupo

# Definir a paleta de cores 'gist_ncar'
palette = sns.color_palette("gist_ncar", n_colors=len(unique_conditions))

# Definir formas diferentes para cada grupo (ajuste conforme necessário)
markers = {
    'group1': 'o',  # Exemplo de grupo 1
    'group2': 's',  # Exemplo de grupo 2
    'MIXED': 'D',   # Adicione aqui o grupo que estava faltando
    # Adicione outras condições conforme necessário
}

plt.figure(figsize=(10, 8))
sns.set_style("whitegrid")

# Scatter plot dos pontos do PCoA com diferentes formas
for condition in unique_conditions:
    subset = merged_df[merged_df['condition1'] == condition]
    plt.scatter(
        subset['PC1'],
        subset['PC2'],
        label=condition,
        color=palette[list(unique_conditions).index(condition)],
        marker=markers.get(condition, 'o')  # Usar forma padrão se condição não estiver no dicionário
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

# Ajustar o layout
plt.title("PCoA Bray-Curtis (Hellinger) com Elipses de Agrupamento")
plt.xlabel(f"PC1 ({pcoa_results.proportion_explained[0]*100:.2f}%)")
plt.ylabel(f"PC2 ({pcoa_results.proportion_explained[1]*100:.2f}%)")
plt.legend(title="Condition1", bbox_to_anchor=(1.05, 1), loc="upper left")

# Salvar o gráfico em PDF
plt.tight_layout()
plt.savefig("pcoa_bray_curtis_hellinger_elipses.pdf", format="pdf", bbox_inches="tight")
plt.show()
