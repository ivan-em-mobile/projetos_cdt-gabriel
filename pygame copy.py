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
pygame.display.set_caption("Jogo da Memória Pygame")
RELOGIO = pygame.time.Clock()

# Carregar imagens das cartas
caminho_imagens = "imagens"
NOMES_IMAGENS = [
    "imagem1.png", "imagem2.png", "imagem3.png", 
    "imagem4.png", "imagem5.png", "imagem6.png",
]
VERSO_NOME = "verso.png"

# Redimensionar imagens para o tamanho das cartas
TAMANHO_CARTA = (100, 100)

# Carrega o verso da carta uma única vez
try:
    VERSO_CARTA_IMG = pygame.image.load(os.path.join(caminho_imagens, VERSO_NOME))
    VERSO_CARTA_IMG = pygame.transform.scale(VERSO_CARTA_IMG, TAMANHO_CARTA)
except pygame.error as e:
    print(f"ERRO: Não foi possível carregar o verso da carta: {e}")
    exit()

# --- 1. Carregamento de Imagens com IDs (Otimizado) ---
dados_imagens = [] # Armazenará tuplas: (Surface, ID)
for nome_arquivo in NOMES_IMAGENS:
    img_path = os.path.join(caminho_imagens, nome_arquivo)
    try:
        imagem_surface = pygame.image.load(img_path)
        imagem_surface = pygame.transform.scale(imagem_surface, TAMANHO_CARTA)
        
        # Armazena a Surface e o ID (nome do arquivo)
        dados_imagens.append((imagem_surface, nome_arquivo))
    except pygame.error as e:
        print(f"AVISO: Imagem {nome_arquivo} não carregada: {e}")
        
# Cria a lista final de cartas com pares e embaralha
todas_imagens_com_id = dados_imagens * 2 
random.shuffle(todas_imagens_com_id)


# --- 2. Classe para representar cada carta ---
class Carta:
    def __init__(self, imagem_e_id, x, y):
        self.imagem_frente = imagem_e_id[0]
        self.id_par = imagem_e_id[1]        # ID usado para comparação!
        self.imagem_verso = VERSO_CARTA_IMG
        self.rect = pygame.Rect(x, y, TAMANHO_CARTA[0], TAMANHO_CARTA[1])
        self.virada = False
        self.encontrada = False

    def desenhar(self, janela):
        """Desenha a carta na tela, mostrando a frente ou o verso."""
        if self.virada:
            janela.blit(self.imagem_frente, self.rect)
        elif not self.encontrada:
            janela.blit(self.imagem_verso, self.rect)
        # Se 'encontrada' for True, ela não é desenhada, sumindo da tela.

# --- 3. Funções Auxiliares ---

def criar_cartas():
    """Cria e organiza as cartas na tela, usando a lista de IDs embaralhados."""
    cartas = []
    margem_x, margem_y = 50, 50
    espacamento = 20
    cartas_por_linha = 4
    
    for i, img_e_id in enumerate(todas_imagens_com_id):
        linha = i // cartas_por_linha
        coluna = i % cartas_por_linha
        x = margem_x + coluna * (TAMANHO_CARTA[0] + espacamento)
        y = margem_y + linha * (TAMANHO_CARTA[1] + espacamento)
        
        # Passa a tupla (Surface, ID) para a classe Carta
        cartas.append(Carta(img_e_id, x, y))
        
    return cartas

def desenhar_texto(texto, tamanho, cor, x, y):
    """Função para desenhar texto na tela."""
    # Tenta usar uma fonte padrão do Pygame ou a fonte do sistema
    try:
        fonte = pygame.font.Font(None, tamanho)
    except Exception:
        fonte = pygame.font.SysFont("Arial", tamanho)
        
    superficie_texto = fonte.render(texto, True, cor)
    retangulo_texto = superficie_texto.get_rect(center=(x, y))
    JANELA.blit(superficie_texto, retangulo_texto)

# --- 4. Loop Principal do Jogo ---

def game_loop():
    cartas = criar_cartas()
    viradas = []        # Armazena as cartas viradas na rodada atual
    pontos = 0
    jogo_rodando = True
    ultima_jogada = time.time()
    
    # Variável de estado para controlar se estamos esperando o delay de 1 segundo
    aguardando_verificacao = False
    
    while jogo_rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                jogo_rodando = False
            
            # 4a. Tratamento de clique
            if evento.type == pygame.MOUSEBUTTONDOWN:
                # Permite cliques apenas se não estivermos aguardando o delay
                if not aguardando_verificacao:
                    for carta in cartas:
                        # Checa se o clique foi na carta, se ela não está virada E se não foi encontrada
                        if carta.rect.collidepoint(evento.pos) and not carta.virada and not carta.encontrada:
                            carta.virada = True
                            viradas.append(carta)
                            
                            # Se a segunda carta foi virada, inicia o delay
                            if len(viradas) == 2:
                                aguardando_verificacao = True
                                ultima_jogada = time.time() # Registra o momento do segundo clique

        # 4b. Lógica de virar e checar par (executada APÓS o delay)
        if aguardando_verificacao and time.time() - ultima_jogada > 1.0:
            
            # --- O CORAÇÃO da LÓGICA: Comparação pelo ID ---
            if viradas[0].id_par == viradas[1].id_par:
                print("Parabéns! Você fez um par!")
                pontos += 10
                viradas[0].encontrada = True
                viradas[1].encontrada = True
            else:
                print("Ops! Cartas diferentes.")
                viradas[0].virada = False
                viradas[1].virada = False
                
            # Limpa e libera a próxima jogada
            viradas = []
            aguardando_verificacao = False
            
        # 4c. Verificar se o jogo acabou
        cartas_encontradas = sum(1 for carta in cartas if carta.encontrada)
        if cartas_encontradas == len(cartas):
            # Exibir tela de Fim de Jogo
            JANELA.fill(COR_FUNDO)
            desenhar_texto("Fim de Jogo!", 80, COR_TEXTO, LARGURA // 2, ALTURA // 2 - 50)
            desenhar_texto(f"Sua Pontuação Final: {pontos}", 40, COR_TEXTO, LARGURA // 2, ALTURA // 2 + 20)
            pygame.display.flip()
            time.sleep(5) # Delay de 5 segundos antes de fechar (usando sleep é OK aqui)
            jogo_rodando = False

        # 4d. Desenhar tudo na tela
        JANELA.fill(COR_FUNDO)
        for carta in cartas:
            # A carta.desenhar() já cuida de não desenhar as encontradas
            carta.desenhar(JANELA) 
        
        desenhar_texto(f"Pontuação: {pontos}", 30, COR_TEXTO, LARGURA - 100, 30)

        pygame.display.flip()
        RELOGIO.tick(60) # Limita o FPS a 60

    pygame.quit()

if __name__ == "__main__":
    game_loop()