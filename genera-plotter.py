import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import pdfpages
import numpy as np
import os

if not os.path.exists('output_csv'):
    os.makedirs('output_csv')

metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
genus_table = pd.read_csv('exported-table-genus-hellinger/genus-feature-table_noheader.tsv', sep='\t', header=0)

print("nomes das colunas no arquivo feature-table.tsv:", genus_table.columns)

index_column_name = genus_table.columns[0]  # obtem o nome da primeira coluna
genus_table = genus_table.set_index(index_column_name)

def extract_genus_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # verifique se e uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('g__'):
                return part[3:]  # retorna apenas o nome do genero
    return 'unknown'  # retorna 'unknown' se nao encontrar ou se nao for string

genus_table.index = [extract_genus_name(name) for name in genus_table.index]
genus_table = genus_table.groupby(genus_table.index).sum()

genus_table = genus_table.t

genus_table = genus_table.join(metadata['condition1'])

genus_grouped = genus_table.groupby('condition1').sum()

genus_relative = genus_grouped.div(genus_grouped.sum(axis=1), axis=0) * 100

def group_others(row, threshold=1.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['others < 1%'] = others
    return row

genus_relative_with_others = genus_relative.apply(group_others, axis=1)

columns = [col for col in genus_relative_with_others.columns if col != 'others < 1%'] + ['others < 1%']
genus_relative_with_others = genus_relative_with_others[columns]

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

others_color = "gray"

unique_genera = genus_table.columns.tolist()
if 'condition1' in unique_genera:
    unique_genera.remove('condition1')  # remover a coluna de condicao, se presente

color_mapping = {genus: colors_list[i % len(colors_list)] for i, genus in enumerate(unique_genera)}
color_mapping['others < 1%'] = others_color  # atribuir cinza para 'others < 1%'

with pdfpages('stacked_bar_plots-genus.pdf') as pdf:
    num_conditions = len(genus_relative_with_others.index)
    
    # ajustar o tamanho da figura com base no numero de condicoes (proporcao 16:9)
    figsize_width = 16
    figsize_height = max(9, num_conditions * 0.4)  # ajuste dinamico da altura

    fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
    
    genus_relative_with_others.plot(kind='bar', stacked=true, ax=ax, color=[color_mapping[genus] for genus in genus_relative_with_others.columns])
    
    ax.set_title('abundancia de generos por condicao', fontsize=16)
    ax.set_ylabel('abundancia relativa (%)', fontsize=14)
    ax.set_xlabel('condicao', fontsize=14)
    ax.tick_params(axis='x', labelsize=12, rotation=45)  # rotacionar os rotulos do eixo x para melhor legibilidade
    
    # ajustar a legenda para caber todos os elementos
    legend = ax.legend(title='genero', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10, ncol=1)
    legend.set_title('genero', prop={'size': 12})
    
    plt.subplots_adjust(right=0.75)  # ajustar margens

    # adicionar rotulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0.5:  # mostrar rotulos apenas para valores maiores que 0.5%
            ax.annotate(f'{value:.1f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + value/2),
                        ha='center', va='center', fontsize=8, color='black')

    pdf.savefig(fig, bbox_inches='tight') # remove bordas desnecessarias ao salvar no pdf
    plt.close(fig)

with pdfpages('pie_charts_by_condition-genus.pdf') as pdf:
    for condition in genus_relative_with_others.index:
        sizes = genus_relative_with_others.loc[condition].dropna()
        
        # agrupar valores abaixo de 1%
        sizes_above_threshold = sizes[sizes >= 1]
        others_size = sizes[sizes < 1].sum()

        if others_size > 0:
            sizes_above_threshold['others < 1%'] = others_size

        if sizes_above_threshold.sum() > 0:  # verificar se ha dados validos apos o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[genus] for genus in sizes_above_threshold.index])
            plt.title(f'composicao de generos para {condition}')
            plt.ylabel('')  # remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

genus_overall = genus_table.drop(columns='condition1', errors='ignore').sum()
genus_overall_relative = (genus_overall / genus_overall.sum()) * 100

with pdfpages('overall_pie_chart-genus.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = genus_overall_relative[genus_overall_relative >= 1]
    others_size_overall = genus_overall_relative[genus_overall_relative < 1].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['others < 1%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=true) # remover nans se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[genus] for genus in sizes_overall_above_threshold.index])
    
    plt.title('composicao geral de generos')
    plt.ylabel('')  # remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

genus_grouped.to_excel('genus_abundance_by_condition-genus.xlsx')
genus_overall_df = genus_overall.to_frame(name='overall abundance')
genus_overall_df['overall relative abundance (%)'] = genus_overall_relative
genus_overall_df.to_excel('overall_genus_abundance-genus.xlsx')

for condition in genus_grouped.index:
    # abundancias brutas
    abundance_df = genus_grouped.loc[condition].to_frame(name='abundance')
    
    # abundancias relativas
    relative_abundance_df = genus_relative.loc[condition].to_frame(name='relative abundance (%)')
    
    # combinar as duas tabelas
    combined_df = pd.concat([abundance_df, relative_abundance_df], axis=1)
    
    # salvar em um arquivo .csv
    combined_df.to_csv(f'output_csv/{condition}_abundances.csv')

print("analise concluida. os resultados foram salvos em arquivos pdf, excel e csv.")
