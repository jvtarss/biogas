import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Carregar os dados
pathway_table = pd.read_csv('pathways-table.tsv_noheader.tsv', sep='\t', index_col=0)
metadata = pd.read_csv('/home/ubuntu/biogas/metadata-combined.tsv', sep='\t', index_col='sample-id')

# Verificar as primeiras linhas da tabela de vias metabólicas
print("Primeiras linhas da tabela de vias metabólicas:")
print(pathway_table.head())

# Verificar as primeiras linhas dos metadados
print("\nPrimeiras linhas dos metadados:")
print(metadata.head())

# Transpor a tabela de vias metabólicas para que as amostras sejam as linhas
pathway_table = pathway_table.T

# Adicionar a coluna 'condition1' aos dados transpostos
pathway_table = pathway_table.join(metadata['condition1'])

# Agrupar por 'condition1' e somar as abundâncias
pathway_grouped = pathway_table.groupby('condition1').sum()

# Calcular abundâncias relativas (0-100%)
pathway_relative = pathway_grouped.div(pathway_grouped.sum(axis=1), axis=0) * 100

# Selecionar as 20 vias metabólicas mais abundantes em todas as condições
top_20_pathways = pathway_relative.sum().sort_values(ascending=False).head(20).index
pathway_relative_top20 = pathway_relative[top_20_pathways]

# Lista de cores (garantir que haja cores suficientes)
colors_list = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink"
]

# Criar gráficos de barras empilhadas
with PdfPages('stacked_bar_plots-pathways.pdf') as pdf:
    ax = pathway_relative_top20.plot(kind='bar', stacked=True, figsize=(12, 8), color=colors_list)
    plt.title('Abundância das 20 Maiores Vias Metabólicas por Condição')
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

# Exportar abundâncias brutas e relativas de todas as amostras
pathway_abundance_all_samples = pathway_table.drop(columns='condition1', errors='ignore')
pathway_abundance_all_samples_relative = pathway_abundance_all_samples.div(pathway_abundance_all_samples.sum(axis=1), axis=0) * 100

# Salvar em Excel
with pd.ExcelWriter('pathway_abundance_all_samples.xlsx') as writer:
    pathway_abundance_all_samples.to_excel(writer, sheet_name='Abundâncias Brutas')
    pathway_abundance_all_samples_relative.to_excel(writer, sheet_name='Abundâncias Relativas')

# Exportar abundâncias brutas e relativas agrupadas por 'condition1'
with pd.ExcelWriter('pathway_abundance_by_condition.xlsx') as writer:
    pathway_grouped.to_excel(writer, sheet_name='Abundâncias Brutas')
    pathway_relative.to_excel(writer, sheet_name='Abundâncias Relativas')

print("Análise concluída. Os resultados foram salvos em arquivos PDF e Excel.")
