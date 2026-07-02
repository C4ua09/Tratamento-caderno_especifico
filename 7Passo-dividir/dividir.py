from PIL import Image
import os
Image.MAX_IMAGE_PIXELS = None

def converter_cor_gimp_para_rgb(gimp_r, gimp_g, gimp_b):
    """
    Converte valores do GIMP (0-100) para RGB (0-255)
    """
    r = int((gimp_r / 100) * 255)
    g = int((gimp_g / 100) * 255)
    b = int((gimp_b / 100) * 255)
    return (r, g, b)

def encontrar_faixa_cinza(imagem, cor_alvo=(58, 58, 58), tolerancia=15, altura_base=135, margem_erro=5):
    """
    Encontra posições onde há uma faixa horizontal cinza com altura aproximada
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    posicoes_corte = []
    
    # Altura mínima e máxima baseada na margem de erro (130 a 140 pixels)
    altura_minima = altura_base - margem_erro
    altura_maxima = altura_base + margem_erro
    
    y = 0
    while y < altura - altura_minima:
        pixels_consecutivos = 0
        
        while (y + pixels_consecutivos) < altura:
            pixel = pixels[largura-2, y + pixels_consecutivos]
            
            if len(pixel) == 4:
                r, g, b, a = pixel
            else:
                r, g, b = pixel[:3]
            
            if (abs(r - cor_alvo[0]) <= tolerancia and 
                abs(g - cor_alvo[1]) <= tolerancia and 
                abs(b - cor_alvo[2]) <= tolerancia):
                pixels_consecutivos += 1
            else:
                break
        
        if altura_minima <= pixels_consecutivos <= altura_maxima:
            # Mantido: O corte é feito exatamente onde a faixa começa (y)
            posicao_corte = y
                
            posicoes_corte.append((posicao_corte, pixels_consecutivos))
            print(f"Faixa cinza encontrada com altura {pixels_consecutivos}px começando em y={posicao_corte}")
            
            y += pixels_consecutivos
        else:
            y += max(1, pixels_consecutivos)
            
    return posicoes_corte

def dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_alvo):
    """
    Divide a imagem verticalmente cortando ANTES das faixas cinzas para mantê-las no início do bloco seguinte
    """
    imagem = Image.open(caminho_imagem)
    largura, altura = imagem.size
    
    print(f"Imagem carregada: {largura}x{altura} pixels")
    
    dados_corte = encontrar_faixa_cinza(imagem, cor_alvo)
    
    if not dados_corte:
        print("Nenhuma faixa cinza encontrada na imagem com os critérios definidos!")
        return
    
    print(f"Encontradas {len(dados_corte)} faixas cinzas para corte")
    
    os.makedirs(pasta_saida, exist_ok=True)
    
    posicao_anterior = 0
    contador_partes = 1
    
    for i, (posicao_corte, _) in enumerate(dados_corte):
        # CORREÇÃO 1: Evita criar imagens vazias (altura <= 0) se houver uma faixa no topo (y=0)
        if posicao_corte <= posicao_anterior:
            posicao_anterior = posicao_corte
            continue
            
        # Corta o bloco anterior (vai até o início da faixa atual)
        area_corte = (0, posicao_anterior, largura, posicao_corte)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{contador_partes:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")
        
        # CORREÇÃO 2: A próxima seção começa exatamente onde a atual foi cortada (sem subtrair 1)
        posicao_anterior = posicao_corte
        contador_partes += 1
    
    # Corta a seção restante (que começa com a última faixa cinza encontrada e vai até o fim)
    if posicao_anterior < altura:
        area_corte = (0, posicao_anterior, largura, altura)
        secao = imagem.crop(area_corte)
        
        nome_arquivo = f"parte_{contador_partes:03d}.png"
        caminho_completo = os.path.join(pasta_saida, nome_arquivo)
        secao.save(caminho_completo)
        print(f"Salvo: {caminho_completo} ({secao.width}x{secao.height}px)")

if __name__ == "__main__":
    caminho_imagem = "enem_paginas_51_a_101.png"  
    pasta_saida = "questoes_colunas_51_a_101" 
    
    cor_do_padrao = (58, 58, 58)
    print(f"Cor de busca configurada: RGB {cor_do_padrao}")
    
    dividir_imagem_por_faixas(caminho_imagem, pasta_saida, cor_do_padrao)
    print("Divisão concluída!")