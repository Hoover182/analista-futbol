with open('data_loader.py', 'r', encoding='utf-8') as f:
    content = f.read()

print('ESTADOS_EN_JUEGO' in content)
print('ESTADOS_TERMINADOS' in content)
print(content[content.find('ESTADOS'):content.find('ESTADOS')+200])
