import os
from PIL import Image

Image.MAX_IMAGE_PIXELS = None

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_azul(imagem, cor_alvo, tolerancia=15, altura_faixa=10): # ATUALIZAR a altura da faixa
    """
    Encontra posições onde há uma faixa horizontal da cor especificada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Percorre a imagem de cima para baixo
    y = 0
    while y < altura - altura_faixa:
        # Verifica se há uma faixa de 'altura_faixa' pixels da cor alvo
        faixa_encontrada = True
        
        for dy in range(altura_faixa):
            # Pega a cor do pixel atual (verifica no último pixel da linha, ou seja, no canto da imagem)
            pixel = pixels[largura-2, y + dy]  # CORRIGIDO: verificar o pixel próximo ao canto para evitar bordas
            
            if len(pixel) == 4:  # RGBA
                r, g, b, a = pixel
            else:  # RGB
                r, g, b = pixel[:3]
            
            # Verifica se a cor está dentro da tolerância
            if (abs(r - cor_alvo[0]) > tolerancia or 
                abs(g - cor_alvo[1]) > tolerancia or 
                abs(b - cor_alvo[2]) > tolerancia):
                faixa_encontrada = False
                break
        
        if faixa_encontrada:
            # Corta ANTES da faixa cinza (no pixel anterior)
            posicao_corte = y - 13  # CORREÇÃO: definir a variável
            if posicao_corte < 0:  # Evitar posições negativas
                posicao_corte = 0
                
            posicoes_corte.append(posicao_corte)
            print(f"Faixa cinza encontrada começando em y={y}, cortando em y={posicao_corte}")
            # Pula a faixa inteira para evitar detecções múltiplas
            y += altura_faixa
        else:
            y += 1
    
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas
    """
    # Abre a imagem
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    # Encontra as posições das faixas cinzas
    posicoes_corte = encontrar_faixa_azul(imagem, cor_alvo)
    
    if not posicoes_corte:
        print("Nenhuma faixa cinza encontrada na imagem!")
        return
    
    print(f"Encontradas {len(posicoes_corte)} faixas cinzas para corte")
    
    # Cria a pasta de saída se não existir
    os.makedirs(pasta_saida, exist_ok=True)
    
    # Corta as seções da imagem
    posicao_anterior = 0
    
    for i, posicao_corte in enumerate(posicoes_corte):
        # Garantir que a posição de corte é válida
        if posicao_corte <= posicao_anterior:
            continue
            
        # Corta a seção ANTES da faixa cinza (do início anterior até o início da faixa)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        # Salva a imagem cortada
        nome_arquivo = f"parte_{i+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # A próxima seção começa após o final desta faixa cinza
        posicao_anterior = posicao_corte + 10  # Pula a faixa cinza de 10 pixels
    
    # Corta a seção final (após a última faixa cinza)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{len(posicoes_corte)+1:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "enem_paginas_6_a_50.png"  # Substitua pelo caminho da sua imagem
    pasta_saida = "questoes_colunas" # Substitua pelo nome da pasta de saída desejada

    # Define a cor diretamente em RGB (58, 58, 58) para a faixa cinza
    cor_do_padrao = (58, 58, 58) 
    print(f"Cor configurada: RGB {cor_do_padrao}")
    
    # Executa a divisão
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    
    print("Divisão concluída!")