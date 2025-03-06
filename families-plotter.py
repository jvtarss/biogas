import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import pdfpages
import numpy as np

metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
family_table = pd.read_csv('exported-table-family-hellinger/family-feature-table_noheader.tsv', sep='\t', header=0)

print("nomes das colunas no arquivo feature-table.tsv:", family_table.columns)

index_column_name = family_table.columns[0]  # obtem o nome da primeira coluna
family_table = family_table.set_index(index_column_name)

def extract_family_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # verifique se e uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('f__'):
                return part[3:]  # retorna apenas o nome da familia
    return 'unknown'  # retorna 'unknown' se nao encontrar ou se nao for string

family_table.index = [extract_family_name(name) for name in family_table.index]
family_table = family_table.groupby(family_table.index).sum()

family_table = family_table.t

family_table = family_table.join(metadata['condition1'])

family_grouped = family_table.groupby('condition1').sum()

family_relative = family_grouped.div(family_grouped.sum(axis=1), axis=0) * 100

def group_others(row, threshold=1.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['others < 1%'] = others
    return row

family_relative_with_others = family_relative.apply(group_others, axis=1)

columns = [col for col in family_relative_with_others.columns if col != 'others < 1%'] + ['others < 1%']
family_relative_with_others = family_relative_with_others[columns]

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

others_color = "gray"

unique_families = family_relative_with_others.columns.tolist()
if 'others < 1%' in unique_families:
    unique_families.remove('others < 1%')  # remover 'others < 1%' para atribuir cores aos filos

color_mapping = {family: colors_list[i % len(colors_list)] for i, family in enumerate(unique_families)}
color_mapping['others < 1%'] = others_color  # atribuir cinza para 'others < 1%'

with pdfpages('stacked_bar_plots-family.pdf') as pdf:
    num_conditions = len(family_relative_with_others.index)
    num_families = len(family_relative_with_others.columns)
    
    # ajustar o tamanho da figura com base no numero de condicoes e familias (proporcao 16:9)
    figsize_width = 16
    figsize_height = max(9, num_conditions * 0.4)

    # aumentar altura se muitas familias (mas com limite para manter a proporcao)
    if num_families > 20:
        figsize_height += (num_families - 20) * 0.1
        figsize_height = min(figsize_height, figsize_width * 0.6)  # reduzi a proporcao maxima para 0.6

    fig, ax = plt.subplots(figsize=(figsize_width, figsize_height))
    
    family_relative_with_others.plot(kind='bar', stacked=true, ax=ax, color=[color_mapping[family] for family in family_relative_with_others.columns])
    ax.set_title('abundancia de familias por condicao', fontsize=16)
    ax.set_ylabel('abundancia relativa (%)', fontsize=14)
    ax.set_xlabel('condicao', fontsize=14)
    ax.tick_params(axis='x', labelsize=12, rotation=45)  # rotacionar os rotulos do eixo x para melhor legibilidade
    
    # ajustar a legenda para caber todos os elementos
    legend = ax.legend(title='familia', bbox_to_anchor=(1.0, 1), loc='upper left', fontsize=10, ncol=1, borderaxespad=0.1)
    legend.set_title('familia', prop={'size': 12})
    
    plt.subplots_adjust(right=0.73, left=0.07, top=0.93, bottom=0.1) # ajuste mais agressivo das margens

    # adicionar rotulos nas barras
    for n, x in enumerate([*ax.patches]):
        value = x.get_height()
        if value > 0.5:  # mostrar rotulos apenas para valores maiores que 0.5%
            ax.annotate(f'{value:.1f}%',
                        (x.get_x() + x.get_width()/2., x.get_y() + value/2),
                        ha='center', va='center', fontsize=8, color='black')

    pdf.savefig(fig, bbox_inches='tight') # remove bordas desnecessarias
    plt.close(fig)


with pdfpages('pie_charts_by_condition-family.pdf') as pdf:
    for condition in family_relative_with_others.index:
        sizes = family_relative_with_others.loc[condition].dropna()
        
        # agrupar valores abaixo de 1%
        sizes_above_threshold = sizes[sizes >= 1]
        others_size = sizes[sizes < 1].sum()

        if others_size > 0:
            sizes_above_threshold['others < 1%'] = others_size

        if sizes_above_threshold.sum() > 0:  # verificar se ha dados validos apos o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[family] for family in sizes_above_threshold.index])
            plt.title(f'composicao de familias para {condition}')
            plt.ylabel('')  # remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

family_overall = family_table.drop(columns='condition1', errors='ignore').sum()
family_overall_relative = (family_overall / family_overall.sum()) * 100

with pdfpages('overall_pie_chart-family.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = family_overall_relative[family_overall_relative >= 1]
    others_size_overall = family_overall_relative[family_overall_relative < 1].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['others < 1%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=true) # remover nans se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[family] for family in sizes_overall_above_threshold.index])
    
    plt.title('composicao geral de familias')
    plt.ylabel('')  # remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

family_grouped.to_excel('family_abundance_by_condition-family.xlsx')
family_overall_df = family_overall.to_frame(name='overall abundance')
family_overall_df['overall relative abundance (%)'] = family_overall_relative
family_overall_df.to_excel('overall_family_abundance-family.xlsx')

print("analise concluida. os resultados foram salvos em arquivos pdf e excel.")
