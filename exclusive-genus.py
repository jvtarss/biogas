import pandas as pd

genus_table = pd.read_csv('exported-table-genus-hellinger/genus-feature-table_noheader.tsv', sep='\t', index_col=0)

metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')

condition1 = metadata['condition1']

genus_table = genus_table.t

genus_table['condition1'] = condition1

all_samples_genera = genus_table.drop(columns='condition1').columns[genus_table.drop(columns='condition1').gt(0).all()].tolist()

with open("genera_in_all_samples.txt", "w") as file:
    file.write("generos que ocorrem em todas as amostras:\n")
    for genus in all_samples_genera:
        file.write(f"  - {genus}\n")

print("generos que ocorrem em todas as amostras foram salvos em 'genera_in_all_samples.txt'.")

grouped = genus_table.groupby('condition1')

group_genera = {}

for group_name, group_data in grouped:
    # remover a coluna 'condition1' para analise
    group_data = group_data.drop(columns='condition1')
    
    # identificar generos que ocorrem neste grupo (abundancia > 0)
    group_genera[group_name] = group_data.columns[group_data.gt(0).any()].tolist()

common_genera = set(group_genera[list(group_genera.keys())[0]])
for genera in group_genera.values():
    common_genera.intersection_update(genera)

with open("genera_in_all_groups.txt", "w") as file:
    file.write("generos que ocorrem em todos os grupos:\n")
    for genus in common_genera:
        file.write(f"  - {genus}\n")

print("generos que ocorrem em todos os grupos foram salvos em 'genera_in_all_groups.txt'.")
