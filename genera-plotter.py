import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import os

# Criar a pasta 'output_csv' se ela não existir
if not os.path.exists('output_csv'):
    os.makedirs('output_csv')

# Carregar os dados
metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
genus_table = pd.read_csv('exported-table-genus-hellinger/genus-feature-table_noheader.tsv', sep='\t', header=0)

# Imprimir os nomes das colunas para inspeção
print("Nomes das colunas no arquivo feature-table.tsv:", genus_table.columns)

# Definir a primeira coluna como índice usando o nome exato da coluna
index_column_name = genus_table.columns[0]  # Obtém o nome da primeira coluna
genus_table = genus_table.set_index(index_column_name)

# Remover prefixos e manter apenas o nome do gênero
def extract_genus_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # Verifique se é uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('g__'):
                return part[3:]  # Retorna apenas o nome do gênero
    return 'Unknown'  # Retorna 'Unknown' se não encontrar ou se não for string

# Renomear as linhas da tabela de gêneros com os nomes extraídos
genus_table.index = [extract_genus_name(name) for name in genus_table.index]
genus_table = genus_table.groupby(genus_table.index).sum()

# Agrupar amostras por 'condition1'
# Transpor a tabela para que as amostras sejam as linhas
genus_table = genus_table.T

# Adicionar a coluna 'condition1' aos dados transpostos
genus_table = genus_table.join(metadata['condition1'])

# Agrupar por 'condition1' e somar as abundâncias
genus_grouped = genus_table.groupby('condition1').sum()

# Calcular abundâncias relativas (0-100%)
genus_relative = genus_grouped.div(genus_grouped.sum(axis=1), axis=0) * 100

# Função para agrupar valores pequenos em "Others < 1%"
def group_others(row, threshold=1.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['Others < 1%'] = others
    return row

# Aplicar a função para agrupar "Others < 1%" em cada condição
genus_relative_with_others = genus_relative.apply(group_others, axis=1)

# Reordenar as colunas para garantir que "Others < 1%" fique na parte mais baixa
columns = [col for col in genus_relative_with_others.columns if col != 'Others < 1%'] + ['Others < 1%']
genus_relative_with_others = genus_relative_with_others[columns]

# Lista de cores (garantir que haja cores suficientes e remover tons de cinza)
colors_list = [
    "lightcoral", "indianred", "firebrick", "red", "salmon", "coral", "orangered", "peru", 
    "yellow", "yellowgreen", "greenyellow", "chartreuse", "palegreen", "lightblue", "powderblue", 
    "aqua", "dodgerblue", "purple", "violet", "deeppink", "hotpink", "mediumvioletred", "blue", 
    "slateblue", "turquoise", "lightseagreen", "seagreen", "mediumpurple", "orange", "moccasin", 
    "gold", "khaki", "navajowhite", "darkorange", "limegreen", "mediumseagreen", "darkcyan", 
    "steelblue", "mediumslateblue", "darkorchid", "palevioletred", "crimson", "sandybrown", 
    "darkgoldenrod", "darkkhaki", "darkolivegreen", "cadetblue", "cornflowerblue", "mediumturquoise",
    "plum","thistle","lightpink","rosybrown","lightsteelblue","tan","burlywood","wheat"
]

# Cor para 'Others < 1%'
others_color = "gray"

# Criar um mapeamento de cores para garantir consistência entre gráficos
unique_genera = genus_table.columns.tolist()
if 'condition1' in unique_genera:
    unique_genera.remove('condition1')  # Remover a coluna de condição, se presente

# Atribuir cores aos gêneros
color_mapping = {genus: colors_list[i % len(colors_list)] for i, genus in enumerate(unique_genera)}
color_mapping['Others < 1%'] = others_color  # Atribuir cinza para 'Others < 1%'

# Criar gráficos de barras empilhadas
with PdfPages('stacked_bar_plots-genus.pdf') as pdf:
    num_conditions = len(genus_relative_with_others.index)
    
    # Ajustar o tamanho da figura com base no número de condições (proporção 16:9)
    figsize_width = 16
    figsize_height = max(9, num_conditions * 0.4)  # Ajuste dinâmico da altura

    fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
    
    genus_relative_with_others.plot(kind='bar', stacked=True, ax=ax, color=[color_mapping[genus] for genus in genus_relative_with_others.columns])
    
    ax.set_title('Abundância de Gêneros por Condição', fontsize=16)
    ax.set_ylabel('Abundância Relativa (%)', fontsize=14)
    ax.set_xlabel('Condição', fontsize=14)
    ax.tick_params(axis='x', labelsize=12, rotation=45)  # Rotacionar os rótulos do eixo x para melhor legibilidade
    
    # Ajustar a legenda para caber todos os elementos
    legend = ax.legend(title='Gênero', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, ncol=1)
    legend.set_title('Gênero', prop={'size': 12})
    
    plt.subplots_adjust(right=0.75)  # Ajustar margens

    # Adicionar rótulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0.5:  # Mostrar rótulos apenas para valores maiores que 0.5%
            ax.annotate(f'{value:.1f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + value/2),
                        ha='center', va='center', fontsize=8, color='black')

    pdf.savefig(fig, bbox_inches='tight') # Remove bordas desnecessárias ao salvar no PDF
    plt.close(fig)

# Criar gráficos de pizza com filtro para 'Others < 1%'
with PdfPages('pie_charts_by_condition-genus.pdf') as pdf:
    for condition in genus_relative_with_others.index:
        sizes = genus_relative_with_others.loc[condition].dropna()
        
        # Agrupar valores abaixo de 1%
        sizes_above_threshold = sizes[sizes >= 1]
        others_size = sizes[sizes < 1].sum()

        if others_size > 0:
            sizes_above_threshold['Others < 1%'] = others_size

        if sizes_above_threshold.sum() > 0:  # Verificar se há dados válidos após o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[genus] for genus in sizes_above_threshold.index])
            plt.title(f'Composição de Gêneros para {condition}')
            plt.ylabel('')  # Remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

# Calcular abundâncias gerais com filtro para 'Others < 1%'
genus_overall = genus_table.drop(columns='condition1', errors='ignore').sum()
genus_overall_relative = (genus_overall / genus_overall.sum()) * 100

# Criar gráfico de pizza geral com filtro para 'Others < 1%'
with PdfPages('overall_pie_chart-genus.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = genus_overall_relative[genus_overall_relative >= 1]
    others_size_overall = genus_overall_relative[genus_overall_relative < 1].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['Others < 1%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=True) # Remover NaNs se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[genus] for genus in sizes_overall_above_threshold.index])
    
    plt.title('Composição Geral de Gêneros')
    plt.ylabel('')  # Remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# Exportar para Excel com "-genus" no final dos nomes dos arquivos e incluir abundâncias brutas e relativas
genus_grouped.to_excel('genus_abundance_by_condition-genus.xlsx')
genus_overall_df = genus_overall.to_frame(name='Overall Abundance')
genus_overall_df['Overall Relative Abundance (%)'] = genus_overall_relative
genus_overall_df.to_excel('overall_genus_abundance-genus.xlsx')

# Exportar abundâncias brutas e relativas para cada grupo em arquivos .csv
for condition in genus_grouped.index:
    # Abundâncias brutas
    abundance_df = genus_grouped.loc[condition].to_frame(name='Abundance')
    
    # Abundâncias relativas
    relative_abundance_df = genus_relative.loc[condition].to_frame(name='Relative Abundance (%)')
    
    # Combinar as duas tabelas
    combined_df = pd.concat([abundance_df, relative_abundance_df], axis=1)
    
    # Salvar em um arquivo .csv
    combined_df.to_csv(f'output_csv/{condition}_abundances.csv')

print("Análise concluída. Os resultados foram salvos em arquivos PDF, Excel e CSV.")
