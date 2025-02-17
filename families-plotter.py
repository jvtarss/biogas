import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np

# Carregar os dados
metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
family_table = pd.read_csv('exported-table-family-hellinger/family-feature-table_noheader.tsv', sep='\t', header=0)

# Imprimir os nomes das colunas para inspeção
print("Nomes das colunas no arquivo feature-table.tsv:", family_table.columns)

# Definir a primeira coluna como índice usando o nome exato da coluna
index_column_name = family_table.columns[0]  # Obtém o nome da primeira coluna
family_table = family_table.set_index(index_column_name)

# Remover prefixos e manter apenas o nome da família
def extract_family_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # Verifique se é uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('f__'):
                return part[3:]  # Retorna apenas o nome da família
    return 'Unknown'  # Retorna 'Unknown' se não encontrar ou se não for string

# Renomear as linhas da tabela de famílias com os nomes extraídos
family_table.index = [extract_family_name(name) for name in family_table.index]
family_table = family_table.groupby(family_table.index).sum()

# Agrupar amostras por 'condition1'
# Transpor a tabela para que as amostras sejam as linhas
family_table = family_table.T

# Adicionar a coluna 'condition1' aos dados transpostos
family_table = family_table.join(metadata['condition1'])

# Agrupar por 'condition1' e somar as abundâncias
family_grouped = family_table.groupby('condition1').sum()

# Calcular abundâncias relativas (0-100%)
family_relative = family_grouped.div(family_grouped.sum(axis=1), axis=0) * 100

# Função para agrupar valores pequenos em "Others < 1%"
def group_others(row, threshold=1.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['Others < 1%'] = others
    return row

# Aplicar a função para agrupar "Others < 1%" em cada condição
family_relative_with_others = family_relative.apply(group_others, axis=1)

# Reordenar as colunas para garantir que "Others < 1%" fique na parte mais baixa
columns = [col for col in family_relative_with_others.columns if col != 'Others < 1%'] + ['Others < 1%']
family_relative_with_others = family_relative_with_others[columns]

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

# Cor para 'Others < 1%'
others_color = "gray"

# Criar um mapeamento de cores para garantir consistência entre gráficos
unique_families = family_relative_with_others.columns.tolist()
if 'Others < 1%' in unique_families:
    unique_families.remove('Others < 1%')  # Remover 'Others < 1%' para atribuir cores aos filos

# Atribuir cores às famílias
color_mapping = {family: colors_list[i % len(colors_list)] for i, family in enumerate(unique_families)}
color_mapping['Others < 1%'] = others_color  # Atribuir cinza para 'Others < 1%'

# Criar gráficos de barras empilhadas
with PdfPages('stacked_bar_plots-family.pdf') as pdf:
    num_conditions = len(family_relative_with_others.index)
    num_families = len(family_relative_with_others.columns)
    
    # Ajustar o tamanho da figura com base no número de condições e famílias (proporção 16:9)
    figsize_width = 16
    figsize_height = max(9, num_conditions * 0.4)

    # Aumentar altura se muitas famílias (mas com limite para manter a proporção)
    if num_families > 20:
        figsize_height += (num_families - 20) * 0.1
        figsize_height = min(figsize_height, figsize_width * 0.6)  # Reduzi a proporção máxima para 0.6

    fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
    
    family_relative_with_others.plot(kind='bar', stacked=True, ax=ax, color=[color_mapping[family] for family in family_relative_with_others.columns])
    ax.set_title('Abundância de Famílias por Condição', fontsize=16)
    ax.set_ylabel('Abundância Relativa (%)', fontsize=14)
    ax.set_xlabel('Condição', fontsize=14)
    ax.tick_params(axis='x', labelsize=12, rotation=45)  # Rotacionar os rótulos do eixo x para melhor legibilidade
    
    # Ajustar a legenda para caber todos os elementos
    legend = ax.legend(title='Família', bbox_to_anchor=(1.0, 1), loc='upper left', fontsize=10, ncol=1, borderaxespad=0.1)
    legend.set_title('Família', prop={'size': 12})
    
    plt.subplots_adjust(right=0.73, left=0.07, top=0.93, bottom=0.1) # Ajuste mais agressivo das margens

    # Adicionar rótulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0.5:  # Mostrar rótulos apenas para valores maiores que 0.5%
            ax.annotate(f'{value:.1f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + value/2),
                        ha='center', va='center', fontsize=8, color='black')

    pdf.savefig(fig, bbox_inches='tight') # Remove bordas desnecessárias
    plt.close(fig)


# Criar gráficos de pizza com filtro para 'Others < 1%'
with PdfPages('pie_charts_by_condition-family.pdf') as pdf:
    for condition in family_relative_with_others.index:
        sizes = family_relative_with_others.loc[condition].dropna()
        
        # Agrupar valores abaixo de 1%
        sizes_above_threshold = sizes[sizes >= 1]
        others_size = sizes[sizes < 1].sum()

        if others_size > 0:
            sizes_above_threshold['Others < 1%'] = others_size

        if sizes_above_threshold.sum() > 0:  # Verificar se há dados válidos após o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[family] for family in sizes_above_threshold.index])
            plt.title(f'Composição de Famílias para {condition}')
            plt.ylabel('')  # Remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

# Calcular abundâncias gerais com filtro para 'Others < 1%'
family_overall = family_table.drop(columns='condition1', errors='ignore').sum()
family_overall_relative = (family_overall / family_overall.sum()) * 100

# Criar gráfico de pizza geral com filtro para 'Others < 1%'
with PdfPages('overall_pie_chart-family.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = family_overall_relative[family_overall_relative >= 1]
    others_size_overall = family_overall_relative[family_overall_relative < 1].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['Others < 1%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=True) # Remover NaNs se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[family] for family in sizes_overall_above_threshold.index])
    
    plt.title('Composição Geral de Famílias')
    plt.ylabel('')  # Remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

# Exportar para Excel com "-family" no final dos nomes dos arquivos e incluir abundâncias brutas e relativas
family_grouped.to_excel('family_abundance_by_condition-family.xlsx')
family_overall_df = family_overall.to_frame(name='Overall Abundance')
family_overall_df['Overall Relative Abundance (%)'] = family_overall_relative
family_overall_df.to_excel('overall_family_abundance-family.xlsx')

print("Análise concluída. Os resultados foram salvos em arquivos PDF e Excel.")
