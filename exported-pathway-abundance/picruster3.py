import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Carregar os dados
pathway_table = pd.read_csv('pathways-table.tsv_noheader.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('/home/ubuntu/biogas/metadata-combined.tsv', sep='\t', index_col='sample-id')

# Transpor a tabela de vias metabólicas para que as amostras sejam as linhas
pathway_table = pathway_table.T

# Adicionar a coluna 'condition1' aos dados transpostos
pathway_table = pathway_table.join(metadata['condition1'])

# 1. Abundância bruta e relativa entre todas as amostras (soma total)
pathway_abundance_all_samples = pathway_table.drop(columns='condition1', errors='ignore')
pathway_abundance_all_samples_sum = pathway_abundance_all_samples.sum()  # Soma total de todas as amostras
pathway_abundance_all_samples_relative = (pathway_abundance_all_samples_sum / pathway_abundance_all_samples_sum.sum()) * 100  # Abundância relativa

# Salvar em Excel
with pd.ExcelWriter('pathway_abundance_all_samples.xlsx') as writer:
    pathway_abundance_all_samples_sum.to_excel(writer, sheet_name='Abundâncias Brutas')
    pathway_abundance_all_samples_relative.to_excel(writer, sheet_name='Abundâncias Relativas')

# 2. Vias metabólicas que ocorrem apenas em um grupo 'condition1'
pathway_grouped = pathway_table.groupby('condition1').sum()
pathway_unique_to_condition = {}

for condition in pathway_grouped.index:
    # Filtrar vias que só ocorrem nessa condição
    unique_pathways = pathway_grouped.loc[condition][pathway_grouped.loc[condition] > 0]
    # Verificar se a via não ocorre em nenhuma outra condição
    unique_pathways = unique_pathways[unique_pathways.index.isin(pathway_grouped.loc[pathway_grouped.index != condition].sum()[pathway_grouped.loc[pathway_grouped.index != condition].sum() == 0].index)]
    pathway_unique_to_condition[condition] = unique_pathways.index.tolist()

# Salvar em um arquivo .txt
with open('pathways_unique_to_condition.txt', 'w') as file:
    for condition, pathways in pathway_unique_to_condition.items():
        file.write(f"Condição: {condition}\n")
        file.write("\n".join(pathways) + "\n\n")

# 3. Definir as vias de metanogênese e fermentação
methanogenesis_pathways = [
    "METHANOGENESIS-PWY", "METH-ACETATE-PWY", "PWY-5258", "PWY-6830", "PWY-5250", "PWY-8107", 
    "PWY-5259", "PWY-8304", "PWY-5247", "PWY-5260", "PWY-5261", "PWY-5250", "METHFORM-PWY", 
    "PWY-6830", "PWY-5209", "PWY2OBG-1", "METHFORM-PWY"
]

fermentation_pathways = [
    "PWY-5951", "PWY-6390", "PWY-8086", "PWY-5494", "PWY-6391", "PWY-6392", "PWY-5676", 
    "P161-PWY", "PWY-7402", "P124-PWY", "PWY-7401", "PWY-6130", "PWY-8015", "PWY-804", 
    "P122-PWY", "P461-PWY", "ANAEROFRUCAT-PWY", "PWY-8189", "PWY-8188", "PWY-8187", 
    "PWY-6344", "P162-PWY", "PWY-5087", "GLUDEG-II-PWY", "PWY-5088", "PWY-8190", 
    "PWY-8184", "PWY-7767", "PWY-8185", "P163-PWY", "PWY-7685", "PWY-8014", "PWY-8186", 
    "PWY-8017", "PWY-8016", "PWY-8183", "PWY-8377", "FERMENTATION-PWY", "PWY-5109", 
    "P164-PWY", "PWY-5497", "PWY-5938", "PWY-5939", "PWY-8274", "PWY-6389", "PWY-5481", 
    "P41-PWY", "PWY-5096", "PWY-5100", "P142-PWY", "PWY-5482", "PWY-5483", "PWY-5485", 
    "PWY-5537", "PWY-5538", "PWY-5600", "PWY-5768", "PWY3O-440", "PWY-6588", "CENTFERM-PWY", 
    "PWY-6583", "PWY-6883", "PWY-5480", "PWY-5486", "PWY-6587", "PWY-6863", "PWY-7111", 
    "P108-PWY", "PWY-5677", "P125-PWY", "PWY-6396", "PWY-6604", "PWY-6590", "PWY-6594", 
    "PROPFERM-PWY", "PWY4LZ-257"
]

# Filtrar as vias presentes nos dados
methanogenesis_pathways = [pathway for pathway in methanogenesis_pathways if pathway in pathway_grouped.columns]
fermentation_pathways = [pathway for pathway in fermentation_pathways if pathway in pathway_grouped.columns]

# Calcular a abundância total de metanogênese e fermentação por condição
methanogenesis_total = pathway_grouped[methanogenesis_pathways].sum(axis=1)
fermentation_total = pathway_grouped[fermentation_pathways].sum(axis=1)

# Criar um DataFrame com as abundâncias totais
grouped_abundance = pd.DataFrame({
    'Methanogenesis': methanogenesis_total,
    'Fermentation': fermentation_total
})

# Calcular abundâncias relativas
grouped_abundance_relative = grouped_abundance.div(grouped_abundance.sum(axis=1), axis=0) * 100

# 4. Criar gráfico de barras empilhadas
with PdfPages('stacked_bar_plots_grouped.pdf') as pdf:
    ax = grouped_abundance_relative.plot(kind='bar', stacked=True, figsize=(12, 8), color=['#1f77b4', '#ff7f0e'])
    plt.title('Abundância de Vias Metabólicas de Metanogênese e Fermentação por Condição')
    plt.ylabel('Abundância Relativa (%)')
    plt.xlabel('Condição')
    plt.legend(title='Categoria', bbox_to_anchor=(1.05, 1), loc='upper left')

    # Adicionar rótulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0:
            ax.annotate(f'{value:.2f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + x.get_height()/2.),
                        ha='center', va='center', fontsize=8, color='black')

    plt.tight_layout()
    pdf.savefig()
    plt.close()

print("Análise concluída. Os resultados foram salvos em arquivos PDF, Excel e TXT.")
