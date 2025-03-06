import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import pdfpages

pathway_table = pd.read_csv('pathways-table.tsv_noheader.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('/home/ubuntu/biogas/metadata-combined.tsv', sep='\t', index_col='sample-id')

pathway_table = pathway_table.t

pathway_table = pathway_table.join(metadata['condition1'])

pathway_abundance_all_samples = pathway_table.drop(columns='condition1', errors='ignore')
pathway_abundance_all_samples_sum = pathway_abundance_all_samples.sum()  # soma total de todas as amostras
pathway_abundance_all_samples_relative = (pathway_abundance_all_samples_sum / pathway_abundance_all_samples_sum.sum()) * 100  # abundancia relativa

with pd.excelwriter('pathway_abundance_all_samples.xlsx') as writer:
    pathway_abundance_all_samples_sum.to_excel(writer, sheet_name='abundancias brutas')
    pathway_abundance_all_samples_relative.to_excel(writer, sheet_name='abundancias relativas')

pathway_grouped = pathway_table.groupby('condition1').sum()
pathway_unique_to_condition = {}

for condition in pathway_grouped.index:
    # filtrar vias que so ocorrem nessa condicao
    unique_pathways = pathway_grouped.loc[condition][pathway_grouped.loc[condition] > 0]
    # verificar se a via nao ocorre em nenhuma outra condicao
    unique_pathways = unique_pathways[unique_pathways.index.isin(pathway_grouped.loc[pathway_grouped.index != condition].sum()[pathway_grouped.loc[pathway_grouped.index != condition].sum() == 0].index)]
    pathway_unique_to_condition[condition] = unique_pathways.index.tolist()

with open('pathways_unique_to_condition.txt', 'w') as file:
    for condition, pathways in pathway_unique_to_condition.items():
        file.write(f"condicao: {condition}\n")
        file.write("\n".join(pathways) + "\n\n")

methanogenesis_pathways = [
    "methanogenesis-pwy", "meth-acetate-pwy", "pwy-5258", "pwy-6830", "pwy-5250", "pwy-8107", 
    "pwy-5259", "pwy-8304", "pwy-5247", "pwy-5260", "pwy-5261", "pwy-5250", "methform-pwy", 
    "pwy-6830", "pwy-5209", "pwy2obg-1", "methform-pwy"
]

methanogenesis_pathways = [pathway for pathway in methanogenesis_pathways if pathway in pathway_grouped.columns]

methanogenesis_relative = pathway_grouped[methanogenesis_pathways].div(pathway_grouped.sum(axis=1), axis=0) * 100

with pdfpages('stacked_bar_plots_methanogenesis.pdf') as pdf:
    ax = methanogenesis_relative.plot(kind='bar', stacked=true, figsize=(12, 8))
    plt.title('abundancia de vias metabolicas de metanogenese por condicao')
    plt.ylabel('abundancia relativa (%)')
    plt.xlabel('condicao')
    plt.legend(title='vias metabolicas', bbox_to_anchor=(1.05, 1), loc='upper left')

    # adicionar rotulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0:
            ax.annotate(f'{value:.2f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + x.get_height()/2.),
                        ha='center', va='center', fontsize=8, color='black')

    plt.tight_layout()
    pdf.savefig()
    plt.close()

print("analise concluida. os resultados foram salvos em arquivos pdf, excel e txt.")
