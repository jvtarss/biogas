import pandas as pd
import numpy as np

table = pd.read_csv('exported_table/feature-table.tsv', sep='\t', skiprows=1, index_col=0)

hellinger_table = np.sqrt(table.div(table.sum(axis=0), axis=1).fillna(0))

hellinger_table.to_csv('hellinger_table.tsv', sep='\t')
