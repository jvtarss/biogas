import re

# Função para extrair o domínio, filo e família
def extract_taxonomy(label):
    # Extrai o domínio (d__), filo (p__) e família (f__)
    domain_match = re.search(r"d__([^;]+)", label)
    phylum_match = re.search(r"p__([^;]+)", label)
    family_match = re.search(r"f__([^;\]]+)", label)

    domain = domain_match.group(1) if domain_match else None
    phylum = phylum_match.group(1) if phylum_match else None
    family = family_match.group(1) if family_match else None

    return domain, phylum, family

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
            domain, phylum, family = extract_taxonomy(label)

            if domain and phylum and family:
                # Modificar o rótulo para incluir apenas o nome da família
                new_line = f'    label "{family}"\n'
                new_lines.append(new_line)

                # Adicionar o domínio e o filo como atributos
                new_lines.append(f'    domain "{domain}"\n')
                new_lines.append(f'    phyla "{phylum}"\n')
            else:
                # Manter a linha original se não houver domínio, filo ou família
                new_lines.append(line)
    elif line.strip().startswith("p "):  # Remove linhas com o atributo 'p'
        continue  # Ignora a linha com o atributo 'p'
    else:
        new_lines.append(line)

# Salvar o novo conteúdo em um arquivo
with open("fixed_network-family.gml", "w") as file:
    file.writelines(new_lines)

print("Arquivo 'fixed_network-family.gml' gerado com sucesso!")
