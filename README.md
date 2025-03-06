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

