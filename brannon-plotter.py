import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from skbio.stats.ordination import ordinationresults

pcoa_results = ordinationresults.read("exported-pcoa/ordination.txt")
print("shape of pcoa samples:", pcoa_results.samples.shape)
print("pcoa columns:", pcoa_results.samples.columns)

pcoa_df = pd.dataframe(
    pcoa_results.samples.values,
    index=pcoa_results.samples.index,
    columns=[f"pc{i+1}" for i in range(pcoa_results.samples.shape[1])]
)

print("\npcoa dataframe columns after conversion:", pcoa_df.columns)

pcoa_df = pcoa_df.reset_index()
pcoa_df = pcoa_df.rename(columns={'index': 'sample-id'})

metadata = pd.read_csv("metadata-combined.tsv", sep="\t")

merged_df = pcoa_df.merge(metadata, on="sample-id")
print("\nmerged dataframe columns:", merged_df.columns)

unique_conditions = merged_df['condition1'].unique()
print("unique conditions in 'condition1':", unique_conditions)


palette = sns.color_palette("rainbow", n_colors=len(unique_conditions))

markers = ['o', 's', 'd', '^', 'v', '<', '>', 'p', '*', 'x']  # lista de formas disponiveis
marker_dict = {condition: markers[i % len(markers)] for i, condition in enumerate(unique_conditions)}

plt.figure(figsize=(10, 8))
sns.set_style("whitegrid")

for condition in unique_conditions:
    subset = merged_df[merged_df['condition1'] == condition]
    plt.scatter(
        subset['pc1'],
        subset['pc2'],
        label=condition,
        color=palette[list(unique_conditions).index(condition)],
        marker=marker_dict[condition],  # usar forma especifica para cada grupo
        s=100  # tamanho dos pontos
    )

sns.kdeplot(
    data=merged_df,
    x="pc1",
    y="pc2",
    hue="condition1",
    levels=5,
    thresh=0.2,
    palette=palette,
    alpha=0.3
)

plt.title("pcoa bray-curtis (hellinger) com elipses de agrupamento")
plt.xlabel(f"pc1 ({pcoa_results.proportion_explained[0]*100:.2f}%)")
plt.ylabel(f"pc2 ({pcoa_results.proportion_explained[1]*100:.2f}%)")
plt.legend(title="condition1", bbox_to_anchor=(1.05, 1), loc="upper left")

plt.tight_layout()
plt.savefig("pcoa_bray_curtis_hellinger_elipses.pdf", format="pdf", bbox_inches="tight")
plt.show()


alpha_diversity = pd.read_csv("exported-shannon/alpha-diversity.tsv", sep="\t", header=0)
alpha_diversity.columns = ["sample-id", "shannon_entropy"]  # renomear colunas

combined_data = alpha_diversity.merge(metadata, on="sample-id")

plt.figure(figsize=(10, 6))
sns.violinplot(
    x="condition1",  # coluna dos metadados para agrupamento
    y="shannon_entropy",  # coluna de diversidade alfa
    data=combined_data,
    palette=palette,  # usar a mesma paleta de cores do pcoa
    cut=0,  # ajustar a forma dos violinos (nao extrapolar os dados)
    inner="quartile"  # mostrar quartis dentro dos violinos
)

plt.title("diversidade alfa (shannon) por condicao")
plt.xlabel("condicao (condition1)")
plt.ylabel("diversidade alfa (shannon)")
plt.xticks(rotation=45)  # rotacionar rotulos do eixo x, se necessario

plt.tight_layout()
plt.savefig("shannon_violin_plot.pdf", format="pdf")

plt.show()
