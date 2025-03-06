import re

def extract_taxonomy(label):
    # extrai o dominio (d__), filo (p__) e genero (g__)
    domain_match = re.search(r"d__([^;]+)", label)
    phylum_match = re.search(r"p__([^;]+)", label)
    genus_match = re.search(r"g__([^;\]]+)", label)
    
    domain = domain_match.group(1) if domain_match else none
    phylum = phylum_match.group(1) if phylum_match else none
    genus = genus_match.group(1) if genus_match else none
    
    return domain, phylum, genus

with open("network-genus.gml", "r") as file:
    lines = file.readlines()

new_lines = []

for line in lines:
    if "label" in line:
        # extrair o rotulo atual
        label_match = re.search(r'label "([^"]+)"', line)
        if label_match:
            label = label_match.group(1)
            domain, phylum, genus = extract_taxonomy(label)
            
            if domain and phylum and genus:
                # modificar o rotulo para incluir apenas o nome do genero
                new_line = f'    label "{genus}"\n'
                new_lines.append(new_line)
                
                # adicionar o dominio e o filo como atributos
                new_lines.append(f'    domain "{domain}"\n')
                new_lines.append(f'    phyla "{phylum}"\n')
            else:
                # manter a linha original se nao houver dominio, filo ou genero
                new_lines.append(line)
    elif line.strip().startswith("p "):  # remove linhas com o atributo 'p'
        continue  # ignora a linha com o atributo 'p'
    else:
        new_lines.append(line)

with open("fixed_network-genus.gml", "w") as file:
    file.writelines(new_lines)

print("arquivo 'fixed_network-genus.gml' gerado com sucesso!")
