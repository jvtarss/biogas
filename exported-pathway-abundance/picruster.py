import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import pdfpages

pathway_table = pd.read_csv('pathways-table.tsv_noheader.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('/home/ubuntu/biogas/metadata-combined.tsv', sep='\t', index_col='sample-id')

print("primeiras linhas da tabela de vias metabolicas:")
print(pathway_table.head())

print("\nprimeiras linhas dos metadados:")
print(metadata.head())

pathway_table = pathway_table.t

pathway_table = pathway_table.join(metadata['condition1'])

pathway_grouped = pathway_table.groupby('condition1').sum()

pathway_relative = pathway_grouped.div(pathway_grouped.sum(axis=1), axis=0) * 100

top_20_pathways = pathway_relative.sum().sort_values(ascending=false).head(20).index
pathway_relative_top20 = pathway_relative[top_20_pathways]

colors_list = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink"
]

with pdfpages('stacked_bar_plots-pathways.pdf') as pdf:
    ax = pathway_relative_top20.plot(kind='bar', stacked=true, figsize=(12, 8), color=colors_list)
    plt.title('abundancia das 20 maiores vias metabolicas por condicao')
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

pathway_abundance_all_samples = pathway_table.drop(columns='condition1', errors='ignore')
pathway_abundance_all_samples_relative = pathway_abundance_all_samples.div(pathway_abundance_all_samples.sum(axis=1), axis=0) * 100

with pd.excelwriter('pathway_abundance_all_samples.xlsx') as writer:
    pathway_abundance_all_samples.to_excel(writer, sheet_name='abundancias brutas')
    pathway_abundance_all_samples_relative.to_excel(writer, sheet_name='abundancias relativas')

with pd.excelwriter('pathway_abundance_by_condition.xlsx') as writer:
    pathway_grouped.to_excel(writer, sheet_name='abundancias brutas')
    pathway_relative.to_excel(writer, sheet_name='abundancias relativas')

print("analise concluida. os resultados foram salvos em arquivos pdf e excel.")
