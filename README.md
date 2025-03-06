# Análise in silico de dados de sequenciamento amplicon RNAr 16S do NCBI SRA
Este repositório contém os scripts, dados processados e resultados da análise in silico de dados de sequenciamento amplicon RNAr 16S de fermentadores de biogás e biodigestores anaeróbios. O estudo foi realizado entre janeiro e fevereiro de 2025, utilizando 739 amostras de sequenciamento metagenômico selecionadas a partir de 1477 amostras brutas disponíveis no NCBI Sequence Read Archive (SRA).

O objetivo principal deste trabalho foi analisar os perfis microbianos presentes em diferentes fontes de substrato (resíduos urbanos, esterco, substratos sintéticos, silagem e mistos) utilizados para a produção de biogás. As amostras foram agrupadas de acordo com o tipo de biomassa e processadas utilizando a pipeline QIIME2 v2024.5 Amplicon Distribution.

### Metodologia
1. **Processamento de sequencias**:
   - Desmultiplexação e controle de qualidade rigoroso.
   - Remoção de adaptadores, redução de ruídos (denoising) com DADA2, remoção de quimeras e filtragem de sequências de baixa qualidade.
   - Leituras paired-end foram cortadas (203 pb para forward e 150 pb para reverse) e mescladas às single-end.

2. **Classificação taxonômica**:
   - Utilização do classificador GTDB (GTDB r220 full-length sequences) com um limiar de confiança de 0,1.

3. **Análise de diversidade**:
   - Cálculo da diversidade alfa (índice de Shannon) e beta (Bray-Curtis, UniFrac ponderada e não ponderada).
   - Visualização das dissimilaridades via PCoA (análise de componentes principais).

4. **Normalização de dados**:
   - Rarefação (2201 features/ASVs por amostra) e transformação de Hellinger para redução do viés composicional.

5. **Predição funcional**:
   - Utilização do PICRUSt2 para identificação de vias metabólicas associadas à produção de biogás e metanogênese no MetaCyc.
   - 
## Estrutura do reoositorio
O repositório está organizado em arquivos e diretórios que refletem o fluxo de trabalho e os resultados da análise de dados de sequenciamento amplicon RNAr 16S. Abaixo está a descrição da estrutura:
### Arquivos principais
- **README.md**: Este arquivo, que descreve o projeto, a metodologia e a estrutura do repositório.
- **BIOGAS-METADATA-FILTERING-SPREADSHEET.xlsx**: Planilha contendo os metadados filtrados e processados utilizados nas análises.
- **qiime2_log.txt**: Arquivo de log gerado durante a execução das análises no QIIME2.
- **metadata-combined.tsv**, **metadata-filtered.tsv**, **metadata-paired-unique.tsv**, **metadata-single-unique.tsv**, **metadata-single.tsv**: Arquivos de metadados em diferentes estágios de processamento.

### Diretórios
- **exported-pathway-abundance/**: Contém os dados exportados relacionados à abundância de vias metabólicas preditas pelo PICRUSt2.
- **exported-pcoa/**: Arquivos exportados relacionados à análise de coordenadas principais (PCoA) para visualização de dissimilaridades.
- **exported-shannon/**: Resultados exportados da diversidade alfa (índice de Shannon).
- **exported-table-family-hellinger/**, **exported-table-genus-hellinger/**, **exported-table-phyla-hellinger/**: Tabelas de abundância taxonômica (família, gênero e filo) transformadas pelo método de Hellinger.
- **exported-table-phyla/**, **exported-table/**, **exported_table/**: Tabelas de abundância taxonômica em diferentes níveis (filo, gênero, família) e formatos.
- **family-spearman-exported-network/**, **genus-spearman-exported-network/**, **phyla-spearman-exported-network/**: Redes de correlação de Spearman exportadas para níveis taxonômicos de família, gênero e filo.
- **output_csv/**: Arquivos CSV gerados durante as análises, incluindo tabelas de abundância e resultados intermediários.
