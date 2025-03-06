import re

def extract_phylum_and_domain(label):
    # extrai o dominio (d__) e o filo (p__)
    domain_match = re.search(r"d__([^;]+)", label)
    phylum_match = re.search(r"p__([^;\]]+)", label)
    
    domain = domain_match.group(1) if domain_match else none
    phylum = phylum_match.group(1) if phylum_match else none
    
    return domain, phylum

with open("network.gml", "r") as file:
    lines = file.readlines()

new_lines = []

for line in lines:
    if "label" in line:
        # extrair o rotulo atual
        label_match = re.search(r'label "([^"]+)"', line)
        if label_match:
            label = label_match.group(1)
            domain, phylum = extract_phylum_and_domain(label)
            
            if phylum and domain:
                # modificar o rotulo para incluir apenas o nome do filo
                new_line = f'    label "{phylum}"\n'
                new_lines.append(new_line)
                
                # adicionar o dominio como um atributo
                new_lines.append(f'    domain "{domain}"\n')
            else:
                # manter a linha original se nao houver filo ou dominio
                new_lines.append(line)
    else:
        new_lines.append(line)

with open("modified_network.gml", "w") as file:
    file.writelines(new_lines)

print("arquivo 'modified_network.gml' gerado com sucesso!")
