# jogo.py

import pygame
import random
import time
import os

# --- Configurações Iniciais ---
pygame.init()

# Dimensões da tela e cores
LARGURA, ALTURA = 800, 600
COR_FUNDO = (30, 30, 30)
COR_TEXTO = (255, 255, 255)

JANELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo da Memória Divertido")
RELOGIO = pygame.time.Clock()

# Carregar imagens das cartas
caminho_imagens = "imagens"
nomes_imagens = [
    os.path.join(caminho_imagens, "imagem1.png"),
    os.path.join(caminho_imagens, "imagem2.png"),
    os.path.join(caminho_imagens, "imagem3.png"),
    os.path.join(caminho_imagens, "imagem4.png"),
    os.path.join(caminho_imagens, "imagem5.png"),
    os.path.join(caminho_imagens, "imagem6.png"),
]
VERSO_CARTA = pygame.image.load(os.path.join(caminho_imagens, "verso.png"))

# Redimensionar imagens para o tamanho das cartas
TAMANHO_CARTA = (100, 100)
VERSO_CARTA = pygame.transform.scale(VERSO_CARTA, TAMANHO_CARTA)

# --- [CORREÇÃO 1: Carregar imagens com IDs] ---
# Vamos armazenar tuplas (Surface, ID)
dados_imagens = []
for img_path in nomes_imagens:
    # O ID será o nome do arquivo (ex: "imagem1.png")
    id_imagem = os.path.basename(img_path) 
    imagem_surface = pygame.image.load(img_path)
    imagem_surface = pygame.transform.scale(imagem_surface, TAMANHO_CARTA)
    dados_imagens.append((imagem_surface, id_imagem))

# Criar a lista de cartas com pares
todas_imagens_com_id = dados_imagens * 2  # Cria pares de (imagem, id)
random.shuffle(todas_imagens_com_id)

# Classe para representar cada carta
class Carta:
    # --- [CORREÇÃO 2: Aceitar imagem e ID] ---
    def __init__(self, imagem_e_id, x, y):
        self.imagem_frente = imagem_e_id[0] # A imagem Surface
        self.id_par = imagem_e_id[1]        # O identificador (string)
        self.imagem_verso = VERSO_CARTA
        self.rect = pygame.Rect(x, y, TAMANHO_CARTA[0], TAMANHO_CARTA[1])
        self.virada = False
        self.encontrada = False

    def desenhar(self, janela):
        """Desenha a carta na tela, mostrando a frente ou o verso."""
        if self.virada:
            janela.blit(self.imagem_frente, self.rect)
        else:
            janela.blit(self.imagem_verso, self.rect)

# --- Lógica do Jogo ---
def criar_cartas():
    """Cria e organiza as cartas na tela."""
    cartas = []
    margem_x, margem_y = 50, 50
    espacamento = 20
    cartas_por_linha = 4
    
    # --- [CORREÇÃO 3: Usar a lista com IDs] ---
    for i, img_e_id in enumerate(todas_imagens_com_id):
        linha = i // cartas_por_linha
        coluna = i % cartas_por_linha
        x = margem_x + coluna * (TAMANHO_CARTA[0] + espacamento)
        y = margem_y + linha * (TAMANHO_CARTA[1] + espacamento)
        cartas.append(Carta(img_e_id, x, y)) # Passa a tupla (img, id)
        
    return cartas

def desenhar_texto(texto, tamanho, cor, x, y):
    """Função para desenhar texto na tela."""
    fonte = pygame.font.Font(None, tamanho)
    superficie_texto = fonte.render(texto, True, cor)
    retangulo_texto = superficie_texto.get_rect(center=(x, y))
    JANELA.blit(superficie_texto, retangulo_texto)

# --- Loop Principal do Jogo ---
def game_loop():
    cartas = criar_cartas()
    viradas = []  # Armazena as cartas viradas na rodada atual
    pontos = 0
    jogo_rodando = True
    ultima_jogada = time.time()
    
    # Variável para controlar o "delay" antes de virar
    # Precisamos disso para que a lógica de verificação só rode 1s *depois* da segunda carta ser virada
    aguardando_verificacao = False 
    
    while jogo_rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo_rodando = False
            
            # Só permite clicar se não estivermos no meio de uma verificação
            if evento.type == pygame.MOUSEBUTTONDOWN and len(viradas) < 2 and not aguardando_verificacao:
                for carta in cartas:
                    if carta.rect.collidepoint(evento.pos) and not carta.virada and not carta.encontrada:
                        carta.virada = True
                        viradas.append(carta)
                        
                        # Se foi a segunda carta, marca o tempo e ativa a espera
                        if len(viradas) == 2:
                            aguardando_verificacao = True
                            ultima_jogada = time.time()

        # Lógica de virar as cartas
        # Só executa se tivermos 2 cartas viradas e o tempo de espera tiver passado
        if aguardando_verificacao and time.time() - ultima_jogada > 1:
            
            # --- [CORREÇÃO 4: Comparar usando o id_par] ---
            if viradas[0].id_par == viradas[1].id_par:
                print("Parabéns! Você fez um par!")
                pontos += 10
                # Marcar cartas como encontradas
                viradas[0].encontrada = True
                viradas[1].encontrada = True
            else:
                print("Ops! Cartas diferentes.")
                # Virar as cartas de volta
                viradas[0].virada = False
                viradas[1].virada = False
            
            # Limpar a lista de viradas e resetar a espera
            viradas = []
            aguardando_verificacao = False
            
        # Verificar se o jogo acabou
        cartas_encontradas = sum(1 for carta in cartas if carta.encontrada)
        if cartas_encontradas == len(cartas):
            JANELA.fill(COR_FUNDO)
            desenhar_texto("Fim de Jogo!", 80, COR_TEXTO, LARGURA // 2, ALTURA // 2 - 50)
            desenhar_texto(f"Sua Pontuação Final: {pontos}", 40, COR_TEXTO, LARGURA // 2, ALTURA // 2 + 20)
            pygame.display.flip()
            time.sleep(5)
            jogo_rodando = False

        # Desenhar tudo na tela
        JANELA.fill(COR_FUNDO)
        for carta in cartas:
            # Não desenha mais as cartas já encontradas
            if not carta.encontrada:
                carta.desenhar(JANELA)
        
        desenhar_texto(f"Pontuação: {pontos}", 30, COR_TEXTO, LARGURA - 100, 30)

        pygame.display.flip()
        RELOGIO.tick(60)

    pygame.quit()

if __name__ == "__main__":
    game_loop()