import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import pdfpages
import numpy as np

metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')
phyla_table = pd.read_csv('exported-table-phyla-hellinger/phyla-feature-table_noheader.tsv', sep='\t', header=0)

print("nomes das colunas no arquivo feature-table.tsv:", phyla_table.columns)

index_column_name = phyla_table.columns[0]  # obtem o nome da primeira coluna
phyla_table = phyla_table.set_index(index_column_name)

def extract_phylum_name(taxonomy_string):
    if isinstance(taxonomy_string, str):  # verifique se e uma string
        parts = taxonomy_string.split(';')
        for part in parts:
            if part.startswith('p__'):
                return part[3:]  # retorna apenas o nome do filo
    return 'unknown'  # retorna 'unknown' se nao encontrar ou se nao for string

phyla_table.index = [extract_phylum_name(name) for name in phyla_table.index]
phyla_table = phyla_table.groupby(phyla_table.index).sum()

phyla_table = phyla_table.t

phyla_table = phyla_table.join(metadata['condition1'])

phyla_grouped = phyla_table.groupby('condition1').sum()

phyla_relative = phyla_grouped.div(phyla_grouped.sum(axis=1), axis=0) * 100

def group_others(row, threshold=2.0):
    others = row[row < threshold].sum()
    row = row[row >= threshold]
    if others > 0:
        row['others < 2%'] = others
    return row

phyla_relative_with_others = phyla_relative.apply(group_others, axis=1)

columns = [col for col in phyla_relative_with_others.columns if col != 'others < 2%'] + ['others < 2%']
phyla_relative_with_others = phyla_relative_with_others[columns]

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

unique_phyla = phyla_relative_with_others.columns.tolist()
if 'others < 2%' in unique_phyla:
    unique_phyla.remove('others < 2%')  # remover "others < 2%" para atribuir cores aos filos

color_mapping = {phylum: colors_list[i % len(colors_list)] for i, phylum in enumerate(unique_phyla)}
color_mapping['others < 2%'] = others_color  # atribuir cinza para "others < 2%"

with pdfpages('stacked_bar_plots-phyla.pdf') as pdf:
    ax = phyla_relative_with_others.plot(kind='bar', stacked=true, figsize=(12, 8), color=[color_mapping[phylum] for phylum in phyla_relative_with_others.columns])
    plt.title('abundancia de filos por condicao')
    plt.ylabel('abundancia relativa (%)')
    plt.xlabel('condicao')
    plt.legend(title='phylum', bbox_to_anchor=(1.05, 1), loc='upper left')

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

with pdfpages('pie_charts_by_condition-phyla.pdf') as pdf:
    for condition in phyla_relative_with_others.index:
        sizes = phyla_relative_with_others.loc[condition].dropna()
        sizes = sizes[sizes > 0]  # filtrar apenas valores positivos
        
        # agrupar valores abaixo de 2%
        sizes_above_threshold = sizes[sizes >= 2]
        others_size = sizes[sizes < 2].sum()

        if others_size > 0:
            sizes_above_threshold['others < 2%'] = others_size

        if sizes_above_threshold.sum() > 0:  # verificar se ha dados validos apos o filtro
            plt.figure(figsize=(8, 8))
            labels = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_above_threshold.index, sizes_above_threshold)]
            plt.pie(sizes_above_threshold, labels=labels, autopct='', startangle=140, colors=[color_mapping[phylum] for phylum in sizes_above_threshold.index])
            plt.title(f'composicao de filos para {condition}')
            plt.ylabel('')  # remover o label 'y'
            plt.tight_layout()
            pdf.savefig()
            plt.close()

phyla_overall = phyla_table.drop(columns='condition1', errors='ignore').sum()
phyla_overall_relative = (phyla_overall / phyla_overall.sum()) * 100

with pdfpages('overall_pie_chart-phyla.pdf') as pdf:
    plt.figure(figsize=(8, 8))
    
    sizes_overall_above_threshold = phyla_overall_relative[phyla_overall_relative >= 2]
    others_size_overall = phyla_overall_relative[phyla_overall_relative < 2].sum()

    if others_size_overall > 0:
        sizes_overall_above_threshold['others < 2%'] = others_size_overall

    sizes_overall_above_threshold.dropna(inplace=true) # remover nans se houver
    
    labels_overall = [f'{label} ({size:.2f}%)' for label, size in zip(sizes_overall_above_threshold.index, sizes_overall_above_threshold)]
    
    plt.pie(sizes_overall_above_threshold, labels=labels_overall, autopct='', startangle=140, colors=[color_mapping[phylum] for phylum in sizes_overall_above_threshold.index])
    
    plt.title('composicao geral de filos')
    plt.ylabel('')  # remover o label 'y'
    plt.tight_layout()
    pdf.savefig()
    plt.close()

phyla_grouped.to_excel('phyla_abundance_by_condition-phyla.xlsx')
phyla_overall_df = phyla_overall.to_frame(name='overall abundance')
phyla_overall_df['overall relative abundance (%)'] = phyla_overall_relative
phyla_overall_df.to_excel('overall_phyla_abundance-phyla.xlsx')

print("analise concluida. os resultados foram salvos em arquivos pdf e excel.")
