import re
import os

main_path = os.path.expanduser('~/corr-watch-mvp/main.py')
methods_path = os.path.expanduser('~/new_methods.txt')

with open(main_path, 'r') as f:
    content = f.read()

with open(methods_path, 'r') as f:
    new_methods = f.read()

# Regex para encontrar a funcao fetch_data original
pattern = re.compile(r'    def fetch_data\(self, symbol, timeframe=\'1h\', limit=200\):.*?return None', re.DOTALL)

if not pattern.search(content):
    print("ERRO: Nao foi possivel encontrar a funcao fetch_data em main.py")
    exit(1)

updated_content = pattern.sub(new_methods.strip(), content)

with open(main_path, 'w') as f:
    f.write(updated_content)

print("main.py atualizado com sucesso!")
