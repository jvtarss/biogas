import pandas as pd
import subprocess
import os
import shutil

def main():
    # le a lista de amostras dessincronizadas
    with open('unsynced_samples.txt', 'r') as f:
        unsynced_samples = [line.strip() for line in f.readlines() if line.strip() != 'sample id']

    # le os arquivos de metadados
    paired_df = pd.read_csv('metadata-paired-unique.tsv', sep='\t')
    single_df = pd.read_csv('metadata-single-unique.tsv', sep='\t')

    # para cada amostra dessincronizada
    for sample_id in unsynced_samples:
        # encontra a amostra no dataframe paired
        sample_row = paired_df[paired_df['sample-id'] == sample_id]
        
        if not sample_row.empty:
            # extrai o diretorio do autor da amostra do caminho do arquivo
            author = sample_row['author'].iloc[0]
            output_dir = f"samples/{author}"
            
            # cria o diretorio se nao existir
            os.makedirs(output_dir, exist_ok=true)
            
            # remove arquivos paired antigos do diretorio do autor
            old_files = [
                sample_row['forward-absolute-filepath'].iloc[0],
                sample_row['reverse-absolute-filepath'].iloc[0]
            ]
            for file in old_files:
                if os.path.exists(file):
                    os.remove(file)
            
            # define o caminho completo para o novo arquivo
            new_filepath = f"/home/ubuntu/biogas/samples/{author}/{sample_id}_1.fastq.gz"
            
            # baixa novamente como single-end no diretorio correto
            cmd = f"fastq-dump --gzip --outdir {output_dir} {sample_id}"
            subprocess.run(cmd, shell=true)
            
            # renomeia o arquivo se necessario para garantir o padrao _1.fastq.gz
            downloaded_file = f"{output_dir}/{sample_id}.fastq.gz"
            if os.path.exists(downloaded_file):
                os.rename(downloaded_file, new_filepath)
            
            # cria nova linha para o dataframe single
            new_single_row = sample_row.copy()
            new_single_row['type'] = 'single-end'
            new_single_row['absolute-filepath'] = new_filepath
            new_single_row['forward-absolute-filepath'] = ''
            new_single_row['reverse-absolute-filepath'] = ''
            
            # adiciona ao dataframe single
            single_df = pd.concat([single_df, new_single_row], ignore_index=true)
            
            # remove do dataframe paired
            paired_df = paired_df[paired_df['sample-id'] != sample_id]

            print(f"processada amostra {sample_id}: removida do paired e adicionada ao single")

    # salva os arquivos atualizados
    paired_df.to_csv('metadata-paired-unique.tsv', sep='\t', index=false)
    single_df.to_csv('metadata-single-unique.tsv', sep='\t', index=false)

    print("processo concluido!")

if __name__ == "__main__":
    main()
