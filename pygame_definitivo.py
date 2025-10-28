# jogo_memoria_tkinter.py

import tkinter as tk
from tkinter import PhotoImage
import random
import os
from functools import partial

# --- Configurações Iniciais ---
# Nota: O Tkinter prefere PNGs redimensionados e no formato PhotoImage.
# Certifique-se de que suas imagens PNG estão no formato correto.
CAMINHO_IMAGENS = "imagens"
NOMES_IMAGENS = [
    "imagem1.png", "imagem2.png", "imagem3.png", 
    "imagem4.png", "imagem5.png", "imagem6.png",
]
VERSO_NOME = "verso.png"
TAMANHO_CARTA = (100, 100) # Tamanho da imagem, mas o Tkinter usa o tamanho real do arquivo.

# Armazenamento global
todas_imagens = {} # Dicionário: {ID_Imagem: PhotoImage}
cartas = []        # Lista de botões (as cartas)
viradas = []       # Armazena os botões clicados na rodada
pontos = 0
jogadas_bloqueadas = False # Controla o clique durante o atraso

# --- 1. Carregamento de Imagens e Configuração ---

def carregar_imagens():
    """Carrega todas as imagens e prepara a lista de pares com IDs."""
    
    # É crucial que as imagens sejam redimensionadas *antes* de serem usadas
    # pois o PhotoImage do Tkinter não suporta redimensionamento de forma simples.
    # O código assume que suas imagens PNG estão na pasta 'imagens' e no tamanho correto (ex: 100x100).
    
    # Carrega o verso
    try:
        global VERSO_IMAGEM
        verso_path = os.path.join(CAMINHO_IMAGENS, VERSO_NOME)
        VERSO_IMAGEM = PhotoImage(file=verso_path)
    except tk.TclError:
        print(f"ERRO: Não foi possível carregar a imagem de verso em {verso_path}. Verifique o caminho/formato.")
        exit()

    # Carrega as imagens de frente
    lista_de_ids = [] # Vai armazenar os IDs para embaralhar
    for nome_arquivo in NOMES_IMAGENS:
        id_imagem = nome_arquivo
        img_path = os.path.join(CAMINHO_IMAGENS, nome_arquivo)
        
        try:
            # Tkinter PhotoImage
            img_tk = PhotoImage(file=img_path) 
            todas_imagens[id_imagem] = img_tk
            lista_de_ids.append(id_imagem)
            
        except tk.TclError:
            print(f"AVISO: Imagem {nome_arquivo} não encontrada ou formato inválido (use PNG/GIF).")
    
    # Cria a lista final de IDs embaralhados (duplicados para pares)
    global IDs_EMBARALHADOS
    IDs_EMBARALHADOS = lista_de_ids * 2
    random.shuffle(IDs_EMBARALHADOS)

# --- 2. Lógica de Evento (Clique da Carta) ---

def checar_par():
    """Verifica se as duas cartas viradas são um par."""
    global viradas, pontos, jogadas_bloqueadas
    
    # A variável 'id_par' foi armazenada no atributo 'id_carta' do botão
    id1 = viradas[0].id_carta
    id2 = viradas[1].id_carta

    if id1 == id2:
        print("Parabéns! Você fez um par!")
        pontos += 10
        
        # Desabilita e 'destrói' os botões encontrados para simular 'encontrada'
        viradas[0].config(state=tk.DISABLED, relief=tk.SUNKEN)
        viradas[1].config(state=tk.DISABLED, relief=tk.SUNKEN)
        
        # Se quiser fazer as cartas sumirem:
        # viradas[0].grid_forget()
        # viradas[1].grid_forget()
        
        verificar_fim_de_jogo()
        
    else:
        print("Ops! Cartas diferentes.")
        # Vira as cartas de volta para o verso
        viradas[0].config(image=VERSO_IMAGEM)
        viradas[1].config(image=VERSO_IMAGEM)
        
    # Limpa a rodada
    viradas = []
    jogadas_bloqueadas = False # Libera o clique
    atualizar_pontuacao()

def virar_carta(indice_carta):
    """Função chamada quando uma carta é clicada."""
    global viradas, jogadas_bloqueadas
    
    if jogadas_bloqueadas or len(viradas) == 2:
        return # Ignora cliques se o jogo estiver processando ou se já virou duas

    carta_clicada = cartas[indice_carta]

    # Verifica se a carta já está virada ou encontrada
    if carta_clicada in viradas or carta_clicada['state'] == tk.DISABLED:
        return

    # 1. Vira a carta
    id_imagem = carta_clicada.id_carta
    imagem_frente = todas_imagens[id_imagem]
    carta_clicada.config(image=imagem_frente)
    
    # 2. Adiciona à lista de viradas
    viradas.append(carta_clicada)
    
    # 3. Se duas cartas foram viradas, inicia a verificação com atraso
    if len(viradas) == 2:
        jogadas_bloqueadas = True # Bloqueia novos cliques
        # Usa after para criar um atraso (1000ms = 1 segundo)
        root.after(1000, checar_par)

# --- 3. Funções de Layout e Exibição ---

def atualizar_pontuacao():
    """Atualiza o Label de pontuação."""
    lbl_pontuacao.config(text=f"Pontuação: {pontos}")

def verificar_fim_de_jogo():
    """Checa se todas as cartas foram encontradas."""
    
    # Conta quantos botões estão desabilitados (encontrados)
    cartas_encontradas = sum(1 for c in cartas if c['state'] == tk.DISABLED)
    
    if cartas_encontradas == len(cartas):
        # Limpa o grid de cartas (opcional)
        for widget in root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.grid_forget()
                
        # Mostra mensagem de Fim de Jogo
        lbl_fim = tk.Label(root, text="FIM DE JOGO!", font=("Arial", 40), bg='lightgray')
        lbl_fim.grid(row=2, column=0, columnspan=4, pady=20)
        lbl_pontuacao.config(font=("Arial", 20))


def criar_cartas_tkinter(root_window):
    """Cria os botões (cartas) e os posiciona na janela usando grid."""
    
    # Parâmetros de layout
    cartas_por_linha = 4
    colunas = len(NOMES_IMAGENS) * 2 // cartas_por_linha
    
    for i, id_par in enumerate(IDs_EMBARALHADOS):
        linha = i // cartas_por_linha + 1 # Começa na linha 1 (linha 0 é pontuação)
        coluna = i % cartas_por_linha
        
        # Cria o botão que representa a carta
        carta_button = tk.Button(
            root_window,
            image=VERSO_IMAGEM,
            borderwidth=3,
            relief=tk.RAISED,
            # Comando: Usa partial para passar o índice 'i' para a função virar_carta
            command=partial(virar_carta, i)
        )
        
        # Armazena o ID do par no próprio objeto Button (um truque comum no Tkinter)
        carta_button.id_carta = id_par
        
        # Posiciona o botão na grade (grid)
        carta_button.grid(row=linha, column=coluna, padx=5, pady=5)
        
        cartas.append(carta_button)

# --- 4. Inicialização do Jogo ---

if __name__ == "__main__":
    
    # Inicializa a janela principal do Tkinter
    root = tk.Tk()
    root.title("Jogo da Memória Tkinter")
    root.configure(bg='lightgray') # Cor de fundo opcional

    # Carrega as imagens e prepara a lista embaralhada de IDs
    carregar_imagens()
    
    # Cria o Label de Pontuação na Linha 0
    lbl_pontuacao = tk.Label(root, text=f"Pontuação: {pontos}", font=("Arial", 16), bg='lightgray')
    lbl_pontuacao.grid(row=0, column=0, columnspan=4, sticky='w', padx=10, pady=10) # sticky='w' alinha à esquerda

    # Cria todas as cartas (Botões)
    criar_cartas_tkinter(root)
    
    # Inicia o loop principal do Tkinter (similar ao game_loop)
    root.mainloop()