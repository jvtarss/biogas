#!/usr/bin/env python3
import pandas as pd
import subprocess
import os
import shutil

def main():
    # Lê a lista de amostras dessincronizadas
    with open('unsynced_samples.txt', 'r') as f:
        unsynced_samples = [line.strip() for line in f.readlines() if line.strip() != 'Sample ID']

    # Lê os arquivos de metadados
    paired_df = pd.read_csv('metadata-paired-unique.tsv', sep='\t')
    single_df = pd.read_csv('metadata-single-unique.tsv', sep='\t')

    # Para cada amostra dessincronizada
    for sample_id in unsynced_samples:
        # Encontra a amostra no DataFrame paired
        sample_row = paired_df[paired_df['sample-id'] == sample_id]
        
        if not sample_row.empty:
            # Extrai o diretório do autor da amostra do caminho do arquivo
            author = sample_row['author'].iloc[0]
            output_dir = f"samples/{author}"
            
            # Cria o diretório se não existir
            os.makedirs(output_dir, exist_ok=True)
            
            # Remove arquivos paired antigos do diretório do autor
            old_files = [
                sample_row['forward-absolute-filepath'].iloc[0],
                sample_row['reverse-absolute-filepath'].iloc[0]
            ]
            for file in old_files:
                if os.path.exists(file):
                    os.remove(file)
            
            # Define o caminho completo para o novo arquivo
            new_filepath = f"/home/ubuntu/biogas/samples/{author}/{sample_id}_1.fastq.gz"
            
            # Baixa novamente como single-end no diretório correto
            cmd = f"fastq-dump --gzip --outdir {output_dir} {sample_id}"
            subprocess.run(cmd, shell=True)
            
            # Renomeia o arquivo se necessário para garantir o padrão _1.fastq.gz
            downloaded_file = f"{output_dir}/{sample_id}.fastq.gz"
            if os.path.exists(downloaded_file):
                os.rename(downloaded_file, new_filepath)
            
            # Cria nova linha para o DataFrame single
            new_single_row = sample_row.copy()
            new_single_row['type'] = 'SINGLE-END'
            new_single_row['absolute-filepath'] = new_filepath
            new_single_row['forward-absolute-filepath'] = ''
            new_single_row['reverse-absolute-filepath'] = ''
            
            # Adiciona ao DataFrame single
            single_df = pd.concat([single_df, new_single_row], ignore_index=True)
            
            # Remove do DataFrame paired
            paired_df = paired_df[paired_df['sample-id'] != sample_id]

            print(f"Processada amostra {sample_id}: Removida do paired e adicionada ao single")

    # Salva os arquivos atualizados
    paired_df.to_csv('metadata-paired-unique.tsv', sep='\t', index=False)
    single_df.to_csv('metadata-single-unique.tsv', sep='\t', index=False)

    print("Processo concluído!")

if __name__ == "__main__":
    main()
