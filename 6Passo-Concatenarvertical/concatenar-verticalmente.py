from PIL import Image
import os
import re

pasta_imagens = "sem-bordas-externas"
pasta_saida = "concatenadas"
os.makedirs(pasta_saida, exist_ok=True)

# Extrai o número da página
def get_sort_key(nome_arquivo):
    m = re.search(r'pagina_enem_(\d+)', nome_arquivo)
    if m:
        return int(m.group(1))
    return float('inf')

# Lista apenas imagens
arquivos = [
    arq for arq in os.listdir(pasta_imagens)
    if arq.lower().endswith((".png", ".jpg", ".jpeg"))
]

# Ordena pelas páginas
arquivos.sort(key=get_sort_key)

print("Ordem encontrada:")
for arq in arquivos:
    print(arq)

# Abre as imagens
imagens = [Image.open(os.path.join(pasta_imagens, arq)) for arq in arquivos]

# Calcula tamanho da imagem final
largura_max = max(img.width for img in imagens)
altura_total = sum(img.height for img in imagens)

imagem_final = Image.new("RGB", (largura_max, altura_total), "white")

y = 0
for img in imagens:
    imagem_final.paste(img, (0, y))
    y += img.height

saida = os.path.join(pasta_saida, "enem_paginas_51_a_101.png")
imagem_final.save(saida)

print(f"Imagem salva em: {saida}")