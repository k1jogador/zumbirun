import pygame  # Biblioteca para desenvolvimento de jogos em Python
import random  # Biblioteca para geração de números aleatórios
from queue import Queue  # Estrutura de dados para controle de filas
import finder  # Módulo externo para busca de caminho
import copy  # Biblioteca para cópias profundas de estruturas de dados

pygame.init()  # Inicializa a biblioteca pygame
pygame.display.set_caption("Zombie Run")  # Define o título da janela do jogo
grid_tamanho = 40  # Define o tamanho de cada célula da grade do jogo
largura_tela, altura_tela = grid_tamanho * 15, grid_tamanho * 17  # Define a largura e altura da tela do jogo

tela = pygame.display.set_mode((largura_tela, altura_tela))  # Cria a tela do jogo
clock = pygame.time.Clock()  # Cria um relógio para controle da taxa de quadros

restart = True  # Flag para reiniciar o jogo

# Configuração da quantidade de árvores no mapa
quantidade_trees = 60  # Número total de árvores geradas no jogo

# Criação das camadas gráficas
camadaCharacters = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA).convert_alpha()  # Camada para os personagens
camadaChao = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA).convert_alpha()  # Camada para o chão
containerPlayer = pygame.Surface((grid_tamanho, grid_tamanho), pygame.SRCALPHA).convert_alpha()  # Camada para o jogador
containerZombie = pygame.Surface((grid_tamanho, grid_tamanho), pygame.SRCALPHA).convert_alpha()  # Camada para o zumbi
camada_transparente = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)  # Camada transparente para efeitos
camada_transparente.fill((0, 0, 255, 100))  # Define a cor azul com transparência para a camada

# Carregamento e ajuste dos sprites
spriteGrass = pygame.transform.scale(pygame.image.load("source/grass.png"), (grid_tamanho, grid_tamanho))  # Textura de grama
spriteGrassWithFlowers = pygame.transform.scale(pygame.image.load("source/grass_with_flowers.png"), (grid_tamanho, grid_tamanho))  # Textura de grama com flores
spritePlayer = pygame.transform.scale(pygame.image.load("source/player/avatar.png"), (grid_tamanho, grid_tamanho))  # Sprite do jogador
spritePlayerSword = pygame.transform.scale(pygame.image.load("source/player/avatarSword.png"), (grid_tamanho, grid_tamanho))  # Sprite do jogador com espada
spriteZombie = pygame.transform.scale(pygame.image.load("source/mob/zombie.png"), (grid_tamanho, grid_tamanho))  # Sprite do zumbi
spriteTree = pygame.transform.scale(pygame.image.load("source/tree.png"), (grid_tamanho, grid_tamanho))  # Sprite de árvore
spriteTreeIcon = pygame.transform.scale(pygame.image.load("source/treeIcon.png"), (grid_tamanho *1.4, grid_tamanho * 1.4))  # Ícone de árvore
spriteHeart = pygame.transform.scale(pygame.image.load("source/heart.png"), (grid_tamanho, grid_tamanho))  # Sprite do coração (vida)

# Classe do jogador
class Player:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição do jogador no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real em pixels
        self.target_x, self.target_y = self.x, self.y  # Destino do jogador
        self.velocidade = 3  # Velocidade de movimento
        self.moving = False  # Indica se o jogador está em movimento
        self.direction = 'down'  # Direção inicial do jogador
        
        self.madeiras = 0  # Contador de madeiras coletadas
        self.possuiEspada = False  # Indica se o jogador possui uma espada
        
        self.vida = 6  # Vida inicial do jogador
        
        self.dano_timer = 0  # Timer para efeito de dano
        self.cor_original = (255, 255, 255)  # Cor normal
        self.cor_dano = (255, 0, 0)  # Cor ao sofrer dano
        self.cor_atual = self.cor_original  # Cor inicial
    
    def getVida(self):
        return self.vida  # Retorna a vida do jogador

    def getMadeiras(self):
        return self.madeiras  # Retorna a quantidade de madeiras coletadas

    def setMadeiras(self, madeiras):
        self.madeiras = madeiras  # Define a quantidade de madeiras coletadas
    
    def possuiSword(self):
        return self.possuiEspada  # Retorna se o jogador possui uma espada

    def gotSword(self):
        self.possuiEspada = True  # Define que o jogador pegou uma espada
    
    def setVida(self, vida):
        self.vida = vida  # Define a vida do jogador
        self.dano_timer = pygame.time.get_ticks()  # Inicia o timer de dano
        self.cor_atual = self.cor_dano  # Muda a cor para vermelho indicando dano

    def update(self):
        if self.moving:
            dx = self.target_x - self.x  # Calcula a distância no eixo X
            dy = self.target_y - self.y  # Calcula a distância no eixo Y

            if abs(dx) > self.velocidade:
                self.x += self.velocidade if dx > 0 else -self.velocidade
            else:
                self.x = self.target_x

            if abs(dy) > self.velocidade:
                self.y += self.velocidade if dy > 0 else -self.velocidade
            else:
                self.y = self.target_y

            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False  # Interrompe o movimento

        # Verifica se o efeito de dano passou (1 segundo = 1000 ms)
        if self.dano_timer > 0 and pygame.time.get_ticks() - self.dano_timer > 1000:
            self.cor_atual = self.cor_original  # Retorna à cor normal
            self.dano_timer = 0  # Reseta o timer


    def move(self, dir_x, dir_y, matrizGrid):
        if not self.moving:  # Só pode mover se não estiver em movimento
            new_x = self.grid_x + dir_x
            new_y = self.grid_y + dir_y
            
            # Verifica se é um movimento válido dentro dos limites do grid
            if 0 <= new_x < 15 and 0 <= new_y < 17 and matrizGrid[new_y][new_x] == " ":
                matrizGrid[self.grid_y][self.grid_x] = " "  # Libera a célula antiga
                matrizGrid[new_y][new_x] = "P"  # Ocupa a nova célula
                
                self.grid_x, self.grid_y = new_x, new_y  # Atualiza a posição no grid
                self.target_x, self.target_y = new_x * grid_tamanho, new_y * grid_tamanho  # Atualiza o destino em pixels
                self.moving = True  # Inicia o movimento
        
                # Define a direção do jogador
                if dir_y < 0:
                    self.direction = 'up'
                elif dir_y > 0:
                    self.direction = 'down'
                elif dir_x < 0:
                    self.direction = 'left'
                elif dir_x > 0:
                    self.direction = 'right'

    def draw(self):
        containerPlayer.fill((0, 0, 0, 0))  # Limpa o container do jogador
        
        # Seleciona o sprite correto baseado se o jogador tem espada
        if self.possuiSword():
            spritePlayerBase = spritePlayerSword
        else:
            spritePlayerBase = spritePlayer

        # Rotaciona o sprite do jogador de acordo com sua direção
        if self.direction == 'up':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 270)
        elif self.direction == 'down':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 90)
        elif self.direction == 'left':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 0)
        elif self.direction == 'right':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 180)
        
        # Aplica o efeito de cor ao jogador ao sofrer dano
        tinted_sprite = playerDirecaoCorreta.copy()
        tinted_sprite.fill(self.cor_atual, special_flags=pygame.BLEND_MULT)
        
        containerPlayer.blit(tinted_sprite, (0, 0))  # Renderiza o jogador no container
        camadaCharacters.blit(containerPlayer, (self.x, self.y))  # Renderiza o jogador na camada de personagens

# Classe do Zumbi
class Zombie:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição do zumbi no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real (em pixels)
        self.target_x, self.target_y = self.x, self.y  # Destino do zumbi
        self.velocidade = 2  # Velocidade de movimento
        self.moving = False  # Indica se o zumbi está em movimento
        self.direction = 'down'  # Direção inicial

        self.vida = 6  # Vida do zumbi

        self.dano_timer = 0  # Timer para efeito de dano
        self.cor_original = (255, 255, 255)  # Cor normal
        self.cor_dano = (255, 0, 0)  # Cor ao sofrer dano
        self.cor_atual = self.cor_original  # Cor inicial

    def getVida(self):
        return self.vida  # Retorna a vida do zumbi

    def setVida(self, vida):
        self.vida = vida  # Define a nova vida do zumbi
        self.dano_timer = pygame.time.get_ticks()  # Inicia o timer de dano
        self.cor_atual = self.cor_dano  # Altera a cor para vermelho indicando dano

    def draw(self):
        containerZombie.fill((0, 0, 0, 0))  # Limpa o container do zumbi
        
        # Rotaciona o sprite do zumbi conforme a direção
        if self.direction == 'up':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 270)
        elif self.direction == 'down':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 90)
        elif self.direction == 'left':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 0)
        elif self.direction == 'right':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 180)

        # Aplica o efeito de cor ao zumbi quando sofre dano
        tinted_sprite = zombieDirecaoCorreta.copy()
        tinted_sprite.fill(self.cor_atual, special_flags=pygame.BLEND_MULT)

        containerZombie.blit(tinted_sprite, (0, 0))  # Renderiza o zumbi no container
        camadaCharacters.blit(containerZombie, (self.x, self.y))  # Renderiza o zumbi na camada de personagens

    def calcularProximoPasso(self, matriz):
        matrizCopia = finder.find(copy.deepcopy(matriz))  # Copia a matriz e aplica o algoritmo de busca
        dir_x = 0
        dir_y = 0

        # Define a direção baseada na busca do caminho
        if self.grid_x < 14 and matrizCopia[self.grid_y][self.grid_x + 1] == 'X':
            dir_x = 1
            dir_y = 0
        elif self.grid_x > 0 and matrizCopia[self.grid_y][self.grid_x - 1] == 'X':
            dir_x = -1
            dir_y = 0
        elif self.grid_y < 16 and matrizCopia[self.grid_y + 1][self.grid_x] == 'X':
            dir_x = 0
            dir_y = 1
        elif self.grid_y > 0 and matrizCopia[self.grid_y - 1][self.grid_x] == 'X':
            dir_x = 0
            dir_y = -1

        return dir_x, dir_y  # Retorna a direção calculada

    # Função responsável por atualizar o movimento do personagem ou objeto
    def update(self):
        if self.moving:
            # Calcula a diferença entre a posição atual e o destino
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            # Movimenta o personagem na direção do destino, mas limita a velocidade
            if abs(dx) > self.velocidade:
                self.x += self.velocidade if dx > 0 else -self.velocidade
            else:
                self.x = self.target_x  # Corrige para exato quando estiver próximo

            # Movimenta na direção Y da mesma forma
            if abs(dy) > self.velocidade:
                self.y += self.velocidade if dy > 0 else -self.velocidade
            else:
                self.y = self.target_y  # Corrige para exato quando estiver próximo

            # Se o personagem chegou ao destino, finaliza o movimento
            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False  # Finaliza movimento

        # Verifica se o tempo do efeito de dano passou (1 segundo = 1000 ms)
        if self.dano_timer > 0 and pygame.time.get_ticks() - self.dano_timer > 1000:
            self.cor_atual = self.cor_original  # Retorna à cor normal
            self.dano_timer = 0  # Reseta o temporizador de dano

        
    # Função para mover o personagem baseado em um grid
    def move(self, matrizGrid):
        # Calcula o próximo passo a ser dado
        dir_x, dir_y = self.calcularProximoPasso(matrizGrid)

        if not self.moving:  # Só pode mover se não estiver em movimento
            # Calcula as novas posições no grid
            new_x = self.grid_x + dir_x
            new_y = self.grid_y + dir_y
            
            # Verifica se o movimento é válido dentro dos limites do grid
            if 0 <= new_x < 15 and 0 <= new_y < 17 and matrizGrid[new_y][new_x] == " ":
                # Atualiza a matriz liberando a célula antiga e ocupando a nova
                matrizGrid[self.grid_y][self.grid_x] = " "
                matrizGrid[new_y][new_x] = "Z"  # Representação do personagem no grid
                
                # Atualiza as coordenadas no grid e o destino para o movimento
                self.grid_x, self.grid_y = new_x, new_y
                self.target_x, self.target_y = new_x * grid_tamanho, new_y * grid_tamanho
                self.moving = True  # Inicia movimento

                # Determina a direção do movimento
                if dir_y < 0:
                    self.direction = 'up'
                elif dir_y > 0:
                    self.direction = 'down'
                elif dir_x < 0:
                    self.direction = 'left'
                elif dir_x > 0:
                    self.direction = 'right'

# Função para desenhar a grama no grid, com uma variação de flores
def drawGrass(x, y, variacao):
    # Desenha o sprite de grama na posição especificada
    camadaChao.blit(spriteGrass, (x, y))
    if variacao == 1:  # Se a variação for igual a 1, adiciona flores
        camadaChao.blit(spriteGrassWithFlowers, (x, y))

# Função para desenhar uma árvore com rotação, de acordo com a orientação especificada
def drawTree(x, y, matriz, rotacao):
    # Roda o sprite da árvore pela quantidade de rotação especificada
    spriteTreeRodar = pygame.transform.rotate(spriteTree, rotacao)
    camadaCharacters.blit(spriteTreeRodar, (x*grid_tamanho, y*grid_tamanho))

# Função para atualizar a HUD (Heads-Up Display), exibindo informações do jogador
def atualizarHUD(player):
    # Cria a fonte e renderiza o texto "Zombie Run" centralizado
    fonte = pygame.font.SysFont("Montserrat", 35)
    texto = fonte.render("Zombie Run", True, (0,0,0))
    tela.blit(texto, [(largura_tela - texto.get_width()) / 2, 5])

    # Desenha o ícone de árvore na tela
    tela.blit(spriteTreeIcon, (0, altura_tela - grid_tamanho * 1.4))
    
    fonte = pygame.font.SysFont("Montserrat", 22)
    # Exibe o número de madeiras coletadas pelo jogador
    texto = fonte.render(f"{player.getMadeiras()}", True, (0,0,0))
    tela.blit(texto, [grid_tamanho - 5, altura_tela - 20])

    startHeartX = largura_tela - 50
    startHeartY = altura_tela - 50

    # Desenha corações representando a vida do jogador
    for i in range(0, player.getVida(), 1):
        tela.blit(spriteHeart , (startHeartX - 40 * i , startHeartY))

# Função para inicializar o jogo
def startGame():
    rodando = True  # Controla o loop principal do jogo
    matrizGrid = []  # Matriz principal do grid
    matrizGrama = []  # Matriz para variação de grama
    rotacoesTrees = {}  # Dicionário para controlar as rotações das árvores
    clicado = False  # Variável de controle de clique

    # Cria as matrizes do grid e variação de grama
    for num_linhas in range(0, altura_tela // grid_tamanho):
        linhaMatrizBase = []
        linhaMatrizGrama = []

        for num_colunas in range(0, largura_tela // grid_tamanho):
            linhaMatrizBase.append(" ")  # Espaços vazios no grid
            if random.randint(0, 15) == 4:  # Define se haverá flores
                linhaMatrizGrama.append(1)  # Com flores
            else:
                linhaMatrizGrama.append(0)  # Sem flores

        matrizGrid.append(linhaMatrizBase)
        matrizGrama.append(linhaMatrizGrama)

    # Spawn de árvores em posições aleatórias
    for i in range(0, quantidade_trees, 1):
        matrizGrid[random.randint(0,16)][random.randint(0,14)] = "#"

    # Inicializa o player e o zumbi no grid
    player = Player(1, 16)
    matrizGrid[16][1] = 'P'
    zombie = Zombie(1, 1)
    matrizGrid[1][1] = 'Z'

    # Posiciona árvores fixas
    matrizGrid[8][1] = '#'
    matrizGrid[7][5] = '#'
    vidasArvores = {}

    # Loop principal
    while rodando:
        # Define o cursor padrão
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        # Preenche as camadas com cores e imagens
        tela.fill((0, 255, 0))
        tela.blit(camadaChao, (0, 0))
        tela.blit(camadaCharacters, (0, 0))
        camadaCharacters.fill((0, 0, 0, 0))

        # Detecta eventos do Pygame
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        teclasPressionadas = pygame.key.get_pressed()
        if teclasPressionadas[pygame.K_w] or teclasPressionadas[pygame.K_UP]:
            player.move(0, -1, matrizGrid)
        if teclasPressionadas[pygame.K_s] or teclasPressionadas[pygame.K_DOWN]:
            player.move(0, 1, matrizGrid)
        if teclasPressionadas[pygame.K_a] or teclasPressionadas[pygame.K_LEFT]:
            player.move(-1, 0, matrizGrid)
        if teclasPressionadas[pygame.K_d] or teclasPressionadas[pygame.K_RIGHT]:
            player.move(1, 0, matrizGrid)
        # Atualiza a posição dos personagens
        player.update()
        zombie.move(matrizGrid)
        zombie.update()

        # Mecanismo para quebrar árvores
        collider_cursor = pygame.Rect(pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1] , 1 ,1)
        pos_cursor = pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1]
        localizaçãoGridX = pos_cursor[0] // 40
        localizaçãoGridY = pos_cursor[1] // 40


        troncos = []  # Lista para armazenar retângulos que representam árvores
        for y in range(len(matrizGrid)):
            for x in range(len(matrizGrid[y])):
                if matrizGrid[y][x] == '#':  # Verifica se a posição atual é uma árvore
                    # Cria um retângulo invisível para detecção de colisão com a árvore
                    retangulo = pygame.draw.rect(camada_transparente, (0, 0, 255, 0), [x * grid_tamanho, y * grid_tamanho, grid_tamanho, grid_tamanho])
                    troncos.append(retangulo)

        # Verifica se o botão esquerdo do mouse foi solto
        if not pygame.mouse.get_pressed()[0] and clicado == True:
            clicado = False
                    
        for tronco in troncos:
            if collider_cursor.colliderect(tronco):  # Verifica se o cursor colidiu com uma árvore
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)  # Muda o cursor para o formato de mão
                # Verifica se o botão do mouse está pressionado e o jogador está próximo da árvore
                if pygame.mouse.get_pressed()[0] and clicado == False and ((localizaçãoGridX - 1 == player.grid_x and localizaçãoGridY == player.grid_y ) or (player.grid_x == localizaçãoGridX + 1 and localizaçãoGridY == player.grid_y) or (localizaçãoGridY - 1 == player.grid_y and localizaçãoGridX == player.grid_x) or (player.grid_y == localizaçãoGridY + 1 and localizaçãoGridX == player.grid_x)):
                    print("break")

                    # Inicializa a vida da árvore se não houver registro
                    if not (localizaçãoGridX, localizaçãoGridY) in vidasArvores.keys():
                        vidasArvores[(localizaçãoGridX, localizaçãoGridY)] = 3
                    elif vidasArvores[(localizaçãoGridX, localizaçãoGridY)] > 0:  # Diminui a vida da árvore se já existir
                        vidasArvores[(localizaçãoGridX, localizaçãoGridY)] -= 1
                        rotacoesTrees[(localizaçãoGridX, localizaçãoGridY)] = random.randint(0, 360)  # Gera nova rotação
                    elif vidasArvores[(localizaçãoGridX, localizaçãoGridY)] <= 0:  # Remove a árvore se a vida for zero
                        matrizGrid[localizaçãoGridY][localizaçãoGridX] = " "
                        player.setMadeiras(player.getMadeiras() + 1)

                    print(vidasArvores[(localizaçãoGridX, localizaçãoGridY)])
                    clicado = True  # Marca que já houve um clique

        # Desenha a colisão do zumbi para detectar interação
        colliser_zumbi = pygame.draw.rect(camada_transparente, (0, 0, 255, 0), [zombie.grid_x * grid_tamanho, zombie.grid_y * grid_tamanho, grid_tamanho, grid_tamanho])

        if collider_cursor.colliderect(colliser_zumbi):  # Verifica se o cursor colidiu com o zumbi
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            # Verifica se o jogador tem espada e está atacando o zumbi
            if player.possuiSword() and random.randint(0, 3) == 1 and pygame.mouse.get_pressed()[0] and clicado == False and ((localizaçãoGridX - 1 == player.grid_x and localizaçãoGridY == player.grid_y ) or (player.grid_x == localizaçãoGridX + 1 and localizaçãoGridY == player.grid_y) or (localizaçãoGridY - 1 == player.grid_y and localizaçãoGridX == player.grid_x) or (player.grid_y == localizaçãoGridY + 1 and localizaçãoGridX == player.grid_x)):
                zombie.setVida(zombie.getVida() - 1)  # Reduz a vida do zumbi
                clicado = True  # Marca o clique para evitar múltiplos ataques

        # Mecânica para pegar a espada ao coletar 7 madeiras
        if player.getMadeiras() == 7 and not player.possuiSword():
            player.gotSword()
            player.setMadeiras(player.getMadeiras() - 7)

        # Mecânica de ataque do zumbi ao jogador
        if ((zombie.grid_x - 1 == player.grid_x and zombie.grid_y == player.grid_y) or 
            (player.grid_x == zombie.grid_x + 1 and zombie.grid_y == player.grid_y) or 
            (zombie.grid_y - 1 == player.grid_y and zombie.grid_x == player.grid_x) or 
            (player.grid_y == zombie.grid_y + 1 and zombie.grid_x == player.grid_x)):

            # Chance aleatória para o zumbi atacar
            if random.randint(0, 80) == 1:
                player.setVida(player.getVida() - 1)

        # Verifica se a vida do jogador chegou a zero
        if player.getVida() == 0:
            return
        # Verifica se a vida do zumbi chegou a zero (vitória)
        if zombie.getVida() == 0:
            print("Ganhou")
            return

        # Cria uma cópia da matriz para futuras operações
        matrizCola = copy.deepcopy(matrizGrid)

        # Desenha a grama com ou sem variação
        for y in range(len(matrizGrama)):
            for x in range(len(matrizGrama[y])):
                drawGrass(x * grid_tamanho, y * grid_tamanho, matrizGrama[y][x])
        
        # Desenha árvores com suas rotações
        for y in range(len(matrizGrid)):
            for x in range(len(matrizGrid[y])):
                if matrizGrid[y][x] == '#':
                    if not (x, y) in rotacoesTrees.keys():
                        rotacoesTrees[(x, y)] = random.randint(0, 360)  # Gera uma rotação aleatória para a árvore
                    else:
                        drawTree(x, y, matrizGrid, rotacoesTrees[(x, y)])

        # Atualiza a HUD com informações do jogador
        atualizarHUD(player)
        player.draw()  # Desenha o personagem
        zombie.draw()  # Desenha o zumbi
        pygame.display.update()  # Atualiza a tela
        clock.tick(60)  # Controla a taxa de atualização para 60 FPS

    pygame.quit()  # Encerra o Pygame ao sair do loop principal

# Laço para reiniciar o jogo após cada execução
while restart:
    startGame()
