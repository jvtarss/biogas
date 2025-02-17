import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Carregar os dados
metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
phyla_table = pd.read_csv('exported-table-phyla-hellinger/phyla-feature-table_noheader.tsv', sep='\t', header=0)

# Imprimir os nomes das colunas para inspeção
print("Nomes das colunas no arquivo feature-table.tsv:", phyla_table.columns)

# Definir a primeira coluna como índice usando o nome exato da coluna
index_column_name = phyla_table.columns[0]  # Obtém o nome da primeira coluna
phyla_table = phyla_table.set_index(index_column_name)

# Remover "d__Bacteria;" e manter apenas o nome do filo
def extract_phylum_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # Verifique se é uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('p__'):
                return part[3:]  # Retorna apenas o nome do filo
    return 'Unknown'  # Retorna 'Unknown' se não encontrar ou se não for string

# Renomear as linhas da tabela de filos com os nomes extraídos
phyla_table.index = [extract_phylum_name(name) for name in phyla_table.index]
phyla_table = phyla_table.groupby(phyla_table.index).sum()

# Agrupar amostras por 'condition1'
# Transpor a tabela para que as amostras sejam as linhas
phyla_table = phyla_table.T

# Adicionar a coluna 'condition1' aos dados transpostos
phyla_table = phyla_table.join(metadata['condition1'])

# Agrupar por 'condition1' e somar as abundâncias
phyla_grouped = phyla_table.groupby('condition1').sum()

# Calcular abundâncias relativas (0-100%)
phyla_relative = phyla_grouped.div(phyla_grouped.sum(axis=1), axis=0) * 100

# Função para agrupar valores pequenos em "Others < 2%"
def group_others(row, threshold=2.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['Others < 2%'] = others
    return row

# Aplicar a função para agrupar "Others < 2%" em cada condição
phyla_relative_with_others = phyla_relative.apply(group_others, axis=1)

# Reordenar as colunas para garantir que "Others < 2%" fique na parte mais baixa
columns = [col for col in phyla_relative_with_others.columns if col != 'Others < 2%'] + ['Others < 2%']
phyla_relative_with_others = phyla_relative_with_others[columns]

# Lista de cores (garantir que haja cores suficientes e remover tons de cinza)
colors_list = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink", "hotpink", "mediumvioletred", "blue", 
    "slateblue", "turquoise", "lightseagreen", "seagreen", "mediumpurple", "orange", "moccasin", 
    "gold", "khaki", "navajowhite", "darkorange", "limegreen", "mediumseagreen", "darkcyan", 
    "steelblue", "mediumslateblue", "darkorchid", "palevioletred", "crimson", "sandybrown", 
    "darkgoldenrod", "darkkhaki", "darkolivegreen", "cadetblue", "cornflowerblue", "mediumturquoise", 
    "plum", "thistle", "lightpink", "rosybrown", "lightsteelblue", "tan", "burlywood", "wheat"
]

# Cor para 'Others < 2%'
others_color = "gray"

# Criar um mapeamento de cores para garantir consistência entre gráficos
unique_phyla = phyla_relative_with_others.columns.tolist()
if 'Others < 2%' in unique_phyla:
    unique_phyla.remove('Others < 2%')  # Remover "Others < 2%" para atribuir cores aos filos

# Atribuir cores aos filos
color_mapping = {phylum: colors_list[i % len(colors_list)] for i, phylum in enumerate(unique_phyla)}
color_mapping['Others < 2%'] = others_color  # Atribuir cinza para "Others < 2%"

# Criar gráficos de barras empilhadas
with PdfPages('stacked_bar_plots-phyla.pdf') as pdf:
    ax = phyla_relative_with_others.plot(kind='bar', stacked=True, figsize=(12, 8), color=[color_mapping[phylum] for phylum in phyla_relative_with_others.columns])
    plt.title('Abundância de Filos por Condição')
    plt.ylabel('Abundância Relativa (%)')
    plt.xlabel('Condição')
    plt.legend(title='Phylum', bbox_to_anchor=(1.05, 1), loc='upper left')

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

# Criar gráficos de pizza com filtro para 'Others < 2%'
with PdfPages('pie_charts_by_condition-phyla.pdf') as pdf:
    for condition in phyla_relative_with_others.index:
        sizes = phyla_relative_with_others.loc[condition].dropna()
        sizes = sizes[sizes > 0]  # Filtrar apenas valores positivos
        
        # Agrupar valores abaixo de 2%
        sizes_above_threshold = sizes[sizes >= 2]
        others_size = sizes[sizes < 2].sum()

        if others_size > 0:
            sizes_above_threshold['Others < 2%'] = others_size

        if sizes_above_threshold.sum() > 0:  # Verificar se há dados válidos após o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[phylum] for phylum in sizes_above_threshold.index])
            plt.title(f'Composição de Filos para {condition}')
            plt.ylabel('')  # Remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

# Calcular abundâncias gerais com filtro para 'Others < 2%'
phyla_overall = phyla_table.drop(columns='condition1', errors='ignore').sum()
phyla_overall_relative = (phyla_overall / phyla_overall.sum()) * 100

# Criar gráfico de pizza geral com filtro para 'Others < 2%'
with PdfPages('overall_pie_chart-phyla.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = phyla_overall_relative[phyla_overall_relative >= 2]
    others_size_overall = phyla_overall_relative[phyla_overall_relative < 2].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['Others < 2%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=True) # Remover NaNs se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[phylum] for phylum in sizes_overall_above_threshold.index])
    
    plt.title('Composição Geral de Filos')
    plt.ylabel('')  # Remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# Exportar para Excel com "-phyla" no final dos nomes dos arquivos e incluir abundâncias brutas e relativas
phyla_grouped.to_excel('phyla_abundance_by_condition-phyla.xlsx')
phyla_overall_df = phyla_overall.to_frame(name='Overall Abundance')
phyla_overall_df['Overall Relative Abundance (%)'] = phyla_overall_relative
phyla_overall_df.to_excel('overall_phyla_abundance-phyla.xlsx')

print("Análise concluída. Os resultados foram salvos em arquivos PDF e Excel.")
