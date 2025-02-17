import pandas as pd
import numpy as np

# Carregar a tabela de abundância (ignorando o cabeçalho de comentário)
table = pd.read_csv('exported_table/feature-table.tsv', sep='\t', skiprows=1, index_col=0)

# Calcular a soma de cada amostra e as raízes quadradas das proporções (Hellinger)
hellinger_table = np.sqrt(table.div(table.sum(axis=0), axis=1).fillna(0))

# Salvar o resultado
hellinger_table.to_csv('hellinger_table.tsv', sep='\t')
