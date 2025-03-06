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

fermentation_pathways = [
    "pwy-5951", "pwy-6390", "pwy-8086", "pwy-5494", "pwy-6391", "pwy-6392", "pwy-5676", 
    "p161-pwy", "pwy-7402", "p124-pwy", "pwy-7401", "pwy-6130", "pwy-8015", "pwy-804", 
    "p122-pwy", "p461-pwy", "anaerofrucat-pwy", "pwy-8189", "pwy-8188", "pwy-8187", 
    "pwy-6344", "p162-pwy", "pwy-5087", "gludeg-ii-pwy", "pwy-5088", "pwy-8190", 
    "pwy-8184", "pwy-7767", "pwy-8185", "p163-pwy", "pwy-7685", "pwy-8014", "pwy-8186", 
    "pwy-8017", "pwy-8016", "pwy-8183", "pwy-8377", "fermentation-pwy", "pwy-5109", 
    "p164-pwy", "pwy-5497", "pwy-5938", "pwy-5939", "pwy-8274", "pwy-6389", "pwy-5481", 
    "p41-pwy", "pwy-5096", "pwy-5100", "p142-pwy", "pwy-5482", "pwy-5483", "pwy-5485", 
    "pwy-5537", "pwy-5538", "pwy-5600", "pwy-5768", "pwy3o-440", "pwy-6588", "centferm-pwy", 
    "pwy-6583", "pwy-6883", "pwy-5480", "pwy-5486", "pwy-6587", "pwy-6863", "pwy-7111", 
    "p108-pwy", "pwy-5677", "p125-pwy", "pwy-6396", "pwy-6604", "pwy-6590", "pwy-6594", 
    "propferm-pwy", "pwy4lz-257"
]

methanogenesis_pathways = [pathway for pathway in methanogenesis_pathways if pathway in pathway_grouped.columns]
fermentation_pathways = [pathway for pathway in fermentation_pathways if pathway in pathway_grouped.columns]

methanogenesis_total = pathway_grouped[methanogenesis_pathways].sum(axis=1)
fermentation_total = pathway_grouped[fermentation_pathways].sum(axis=1)

grouped_abundance = pd.dataframe({
    'methanogenesis': methanogenesis_total,
    'fermentation': fermentation_total
})

grouped_abundance_relative = grouped_abundance.div(grouped_abundance.sum(axis=1), axis=0) * 100

with pdfpages('stacked_bar_plots_grouped.pdf') as pdf:
    ax = grouped_abundance_relative.plot(kind='bar', stacked=true, figsize=(12, 8), color=['#1f77b4', '#ff7f0e'])
    plt.title('abundancia de vias metabolicas de metanogenese e fermentacao por condicao')
    plt.ylabel('abundancia relativa (%)')
    plt.xlabel('condicao')
    plt.legend(title='categoria', bbox_to_anchor=(1.05, 1), loc='upper left')

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
