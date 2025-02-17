import pandas as pd

# Carregar a tabela de gêneros
genus_table = pd.read_csv('exported-table-genus-hellinger/genus-feature-table_noheader.tsv', sep='\t', index_col=0)

# Carregar os metadados
metadata = pd.read_csv('metadata-combined.tsv', sep='\t', index_col='sample-id')

# Extrair a coluna 'condition1' dos metadados
condition1 = metadata['condition1']

# Transpor a tabela de gêneros para que as amostras sejam as linhas e os gêneros sejam as colunas
genus_table = genus_table.T

# Adicionar a coluna 'condition1' à tabela de gêneros
genus_table['condition1'] = condition1

# 1. Gêneros que ocorrem em absolutamente todas as amostras
# Verificar quais gêneros têm abundância > 0 em todas as amostras
all_samples_genera = genus_table.drop(columns='condition1').columns[genus_table.drop(columns='condition1').gt(0).all()].tolist()

# Salvar os gêneros que ocorrem em todas as amostras
with open("genera_in_all_samples.txt", "w") as file:
    file.write("Gêneros que ocorrem em todas as amostras:\n")
    for genus in all_samples_genera:
        file.write(f"  - {genus}\n")

print("Gêneros que ocorrem em todas as amostras foram salvos em 'genera_in_all_samples.txt'.")

# 2. Gêneros que ocorrem em todos os grupos (condition1)
# Agrupar as amostras por 'condition1'
grouped = genus_table.groupby('condition1')

# Dicionário para armazenar gêneros presentes em cada grupo
group_genera = {}

# Iterar sobre cada grupo
for group_name, group_data in grouped:
    # Remover a coluna 'condition1' para análise
    group_data = group_data.drop(columns='condition1')
    
    # Identificar gêneros que ocorrem neste grupo (abundância > 0)
    group_genera[group_name] = group_data.columns[group_data.gt(0).any()].tolist()

# Identificar gêneros que ocorrem em todos os grupos
common_genera = set(group_genera[list(group_genera.keys())[0]])
for genera in group_genera.values():
    common_genera.intersection_update(genera)

# Salvar os gêneros que ocorrem em todos os grupos
with open("genera_in_all_groups.txt", "w") as file:
    file.write("Gêneros que ocorrem em todos os grupos:\n")
    for genus in common_genera:
        file.write(f"  - {genus}\n")

print("Gêneros que ocorrem em todos os grupos foram salvos em 'genera_in_all_groups.txt'.")
