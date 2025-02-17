import re

# Função para extrair o nome do filo e o domínio
def extract_phylum_and_domain(label):
    # Extrai o domínio (d__) e o filo (p__)
    domain_match = re.search(r"d__([^;]+)", label)
    phylum_match = re.search(r"p__([^;\]]+)", label)
    
    domain = domain_match.group(1) if domain_match else None
    phylum = phylum_match.group(1) if phylum_match else None
    
    return domain, phylum

# Ler o arquivo original
with open("network.gml", "r") as file:
    lines = file.readlines()

# Processar o arquivo e criar um novo conteúdo
new_lines = []

for line in lines:
    if "label" in line:
        # Extrair o rótulo atual
        label_match = re.search(r'label "([^"]+)"', line)
        if label_match:
            label = label_match.group(1)
            domain, phylum = extract_phylum_and_domain(label)
            
            if phylum and domain:
                # Modificar o rótulo para incluir apenas o nome do filo
                new_line = f'    label "{phylum}"\n'
                new_lines.append(new_line)
                
                # Adicionar o domínio como um atributo
                new_lines.append(f'    domain "{domain}"\n')
            else:
                # Manter a linha original se não houver filo ou domínio
                new_lines.append(line)
    else:
        new_lines.append(line)

# Salvar o novo conteúdo em um arquivo
with open("modified_network.gml", "w") as file:
    file.writelines(new_lines)

print("Arquivo 'modified_network.gml' gerado com sucesso!")
