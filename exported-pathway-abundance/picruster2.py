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

# 3. Gráfico de barras empilhadas para vias metabólicas de metanogênese
methanogenesis_pathways = [
    "METHANOGENESIS-PWY", "METH-ACETATE-PWY", "PWY-5258", "PWY-6830", "PWY-5250", "PWY-8107", 
    "PWY-5259", "PWY-8304", "PWY-5247", "PWY-5260", "PWY-5261", "PWY-5250", "METHFORM-PWY", 
    "PWY-6830", "PWY-5209", "PWY2OBG-1", "METHFORM-PWY"
]

# Filtrar as vias de metanogênese presentes nos dados
methanogenesis_pathways = [pathway for pathway in methanogenesis_pathways if pathway in pathway_grouped.columns]

# Calcular abundâncias relativas para as vias de metanogênese
methanogenesis_relative = pathway_grouped[methanogenesis_pathways].div(pathway_grouped.sum(axis=1), axis=0) * 100

# Criar gráfico de barras empilhadas
with PdfPages('stacked_bar_plots_methanogenesis.pdf') as pdf:
    ax = methanogenesis_relative.plot(kind='bar', stacked=True, figsize=(12, 8))
    plt.title('Abundância de Vias Metabólicas de Metanogênese por Condição')
    plt.ylabel('Abundância Relativa (%)')
    plt.xlabel('Condição')
    plt.legend(title='Vias Metabólicas', bbox_to_anchor=(1.05, 1), loc='upper left')

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
