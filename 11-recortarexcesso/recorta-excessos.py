from PIL import Image
import os
import shutil

def encontrar_fim_do_branco(imagem, tolerancia=15):
    """
    Varre a imagem de baixo para cima analisando a linha horizontal quase inteira.
    Evita passar por "buracos" entre as letras e cortar as alternativas.
    """
    largura, altura = imagem.size
    pixels = imagem.load()
    
    # Define uma margem nas laterais para ignorar possíveis bordas pretas/sujeiras do scanner
    margem_lateral = int(largura * 0.1)  # 10% de margem
    x_inicio = margem_lateral
    x_fim = largura - margem_lateral
    
    # Percorre de baixo para cima
    for y in range(altura - 1, -1, -1):
        
        # Varre a linha horizontalmente de x_inicio até x_fim
        for x in range(x_inicio, x_fim):
            pixel = pixels[x, y]
            
            if len(pixel) == 4:
                r, g, b, _ = pixel
            else:
                r, g, b = pixel[:3]
                
            # Se encontrar QUALQUER pixel que não seja branco, achou o fim da página
            if r < (255 - tolerancia) or g < (255 - tolerancia) or b < (255 - tolerancia):
                print(f"Conteúdo detectado na linha y={y}. Cortando abaixo disso.")
                return y + 8  # Margem de segurança de 8 pixels para ficar visualmente agradável
                
    return None

def processar_imagens(pasta_origem, pasta_destino):
    """
    Processa todas as imagens da pasta origem, recortando o excesso branco inferior
    e copiando todas para a pasta destino
    """
    os.makedirs(pasta_destino, exist_ok=True)
    
    arquivos = [f for f in os.listdir(pasta_origem) 
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    print(f"Encontrados {len(arquivos)} arquivos para processar")
    
    for arquivo in arquivos:
        caminho_origem = os.path.join(pasta_origem, arquivo)
        caminho_destino = os.path.join(pasta_destino, arquivo)
        
        try:
            with Image.open(caminho_origem) as imagem:
                print(f"\nProcessando: {arquivo} ({imagem.width}x{imagem.height})")
                
                posicao_corte = encontrar_fim_do_branco(imagem)
                
                if posicao_corte is not None and posicao_corte < imagem.height:
                    area_corte = (0, 0, imagem.width, posicao_corte)
                    imagem_recortada = imagem.crop(area_corte)
                    imagem_recortada.save(caminho_destino)
                    print(f"✓ Imagem recortada: {imagem_recortada.width}x{imagem_recortada.height}")
                else:
                    shutil.copy2(caminho_origem, caminho_destino)
                    print(f"✓ Imagem mantida original (sem excesso branco detectado)")
                    
        except Exception as e:
            print(f"✗ Erro ao processar {arquivo}: {e}")
            try:
                shutil.copy2(caminho_origem, caminho_destino)
                print(f"✓ Arquivo copiado mesmo com erro")
            except:
                print(f"✗ Não foi possível copiar o arquivo")

if __name__ == "__main__":
    pasta_origem = "./questoes"
    pasta_destino = "finalizadas"
    
    print("Iniciando processamento com varredura horizontal completa...")
    
    if not os.path.exists(pasta_origem):
        print(f"Erro: A pasta '{pasta_origem}' não existe!")
        exit(1)
        
    processar_imagens(pasta_origem, pasta_destino)
    print("\n" + "="*50)
    print("Processamento concluído!")