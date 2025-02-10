import pygame
import random
from queue import Queue
import finder
import copy

pygame.init()
pygame.display.set_caption("Zombie Run")
grid_tamanho = 40
largura_tela, altura_tela = grid_tamanho * 15, grid_tamanho * 17

tela = pygame.display.set_mode((largura_tela, altura_tela))
clock = pygame.time.Clock()

restart = True

# Configurações

quantidade_trees = 60




# Camadas 
camadaCharacters = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA).convert_alpha()
camadaChao = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA).convert_alpha()
containerPlayer = pygame.Surface((grid_tamanho, grid_tamanho), pygame.SRCALPHA).convert_alpha()
containerZombie = pygame.Surface((grid_tamanho, grid_tamanho), pygame.SRCALPHA).convert_alpha()
camada_transparente = pygame.Surface((largura_tela, altura_tela), pygame.SRCALPHA)
camada_transparente.fill((0, 0, 255, 100))
# Sprites
spriteGrass = pygame.transform.scale(pygame.image.load("source/grass.png"), (grid_tamanho, grid_tamanho))
spriteGrassWithFlowers = pygame.transform.scale(pygame.image.load("source/grass_with_flowers.png"), (grid_tamanho, grid_tamanho))
spritePlayer = pygame.transform.scale(pygame.image.load("source/player/avatar.png"), (grid_tamanho, grid_tamanho))
spritePlayerSword = pygame.transform.scale(pygame.image.load("source/player/avatarSword.png"), (grid_tamanho, grid_tamanho))
spriteZombie = pygame.transform.scale(pygame.image.load("source/mob/zombie.png"), (grid_tamanho, grid_tamanho))
spriteTree = pygame.transform.scale(pygame.image.load("source/tree.png"), (grid_tamanho, grid_tamanho))
spriteTreeIcon = pygame.transform.scale(pygame.image.load("source/treeIcon.png"), (grid_tamanho *1.4, grid_tamanho * 1.4))
spriteHeart = pygame.transform.scale(pygame.image.load("source/heart.png"), (grid_tamanho, grid_tamanho))

class Player:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real (em pixels)
        self.target_x, self.target_y = self.x, self.y  # Destino
        self.velocidade = 3  # Pixels por frame
        self.moving = False  # Indica se o personagem está em movimento
        self.direction = 'down'

        self.madeiras = 0
        self.possuiEspada = False

        self.vida = 6

        self.dano_timer = 0  # Timer para o efeito de dano
        self.cor_original = (255, 255, 255)  # Cor normal
        self.cor_dano = (255, 0, 0)  # Cor vermelha ao sofrer dano
        self.cor_atual = self.cor_original
    

    def getVida(self):
        return self.vida

    def getMadeiras(self):
        return self.madeiras

    def setMadeiras(self, madeiras):
        self.madeiras = madeiras
    
    def possuiSword(self):
        return self.possuiEspada

    def gotSword(self):
        self.possuiEspada = True


    
    def setVida(self, vida):
        self.vida = vida
        self.dano_timer = pygame.time.get_ticks()  # Inicia o timer de dano
        self.cor_atual = self.cor_dano  # Altera a cor para vermelho

    def update(self):
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            if abs(dx) > self.velocidade:
                self.x += self.velocidade if dx > 0 else -self.velocidade
            else:
                self.x = self.target_x

            if abs(dy) > self.velocidade:
                self.y += self.velocidade if dy > 0 else -self.velocidade
            else:
                self.y = self.target_y

            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False

        # Verifica se o tempo do efeito de dano passou (1 segundo = 1000 ms)
        if self.dano_timer > 0 and pygame.time.get_ticks() - self.dano_timer > 1000:
            self.cor_atual = self.cor_original  # Retorna à cor normal
            self.dano_timer = 0


    def move(self, dir_x, dir_y, matrizGrid):
        if not self.moving:  # Só pode mover se não estiver em movimento
            new_x = self.grid_x + dir_x
            new_y = self.grid_y + dir_y
            
            # Verifica se é um movimento válido dentro dos limites do grid
            if 0 <= new_x < 15 and 0 <= new_y < 17 and matrizGrid[new_y][new_x] == " ":
                matrizGrid[self.grid_y][self.grid_x] = " "  # Libera a célula antiga
                matrizGrid[new_y][new_x] = "P"  # Ocupa a nova célula
                
                self.grid_x, self.grid_y = new_x, new_y
                self.target_x, self.target_y = new_x * grid_tamanho, new_y * grid_tamanho
                self.moving = True  # Inicia movimento
        
                if dir_y < 0:
                    self.direction = 'up'
                elif dir_y > 0:
                    self.direction = 'down'
                elif dir_x < 0:
                    self.direction = 'left'
                elif dir_x > 0:
                    self.direction = 'right'

    def draw(self):
        containerPlayer.fill((0, 0, 0, 0))
        
        if self.possuiSword():
            spritePlayerBase = spritePlayerSword
        else:
            spritePlayerBase = spritePlayer

        if self.direction == 'up':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 270)
        elif self.direction == 'down':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 90)
        elif self.direction == 'left':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 0)
        elif self.direction == 'right':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayerBase, 180)
        
        # Aplica o efeito de cor ao jogador
        tinted_sprite = playerDirecaoCorreta.copy()
        tinted_sprite.fill(self.cor_atual, special_flags=pygame.BLEND_MULT)
        
        containerPlayer.blit(tinted_sprite, (0, 0))
        camadaCharacters.blit(containerPlayer, (self.x, self.y))

class Zombie:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real (em pixels)
        self.target_x, self.target_y = self.x, self.y  # Destino
        self.velocidade = 2  # Pixels por frame
        self.moving = False  # Indica se o personagem está em movimento
        self.direction = 'down'


        self.vida = 6

        self.dano_timer = 0  # Timer para o efeito de dano
        self.cor_original = (255, 255, 255)  # Cor normal
        self.cor_dano = (255, 0, 0)  # Cor vermelha ao sofrer dano
        self.cor_atual = self.cor_original

    def getVida(self):
        return self.vida

    def setVida(self, vida):
        self.vida = vida
        self.dano_timer = pygame.time.get_ticks()  # Inicia o timer de dano
        self.cor_atual = self.cor_dano  # Altera a cor para vermelho

    def draw(self):
        containerZombie.fill((0, 0, 0, 0))  # Limpa o container
        if self.direction == 'up':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 270)
        elif self.direction == 'down':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 90)
        elif self.direction == 'left':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 0)
        elif self.direction == 'right':
            zombieDirecaoCorreta = pygame.transform.rotate(spriteZombie, 180)

        tinted_sprite = zombieDirecaoCorreta.copy()
        tinted_sprite.fill(self.cor_atual, special_flags=pygame.BLEND_MULT)


        containerZombie.blit(tinted_sprite, (0, 0))
        camadaCharacters.blit(containerZombie, (self.x, self.y))

    def calcularProximoPasso(self,matriz):
        matrizCopia = finder.find(copy.deepcopy(matriz))
        dir_x = 0
        dir_y = 0

        if self.grid_x < 14 and matrizCopia[self.grid_y][self.grid_x + 1] == 'X':
            dir_x = 1
            dir_y = 0
        elif self.grid_x > 0 and matrizCopia[self.grid_y][self.grid_x - 1] == 'X':
            dir_x = -1
            dir_y = 0
        elif self.grid_y < 16  and matrizCopia[self.grid_y + 1][self.grid_x] == 'X':
            dir_x = 0
            dir_y = 1
        
        elif self.grid_y > 0 and matrizCopia[self.grid_y - 1][self.grid_x] == 'X':
            dir_x = 0
            dir_y = -1


        return dir_x, dir_y

    def update(self):
        if self.moving:
            dx = self.target_x - self.x
            dy = self.target_y - self.y

            if abs(dx) > self.velocidade:
                self.x += self.velocidade if dx > 0 else -self.velocidade
            else:
                self.x = self.target_x  # Corrige para exato quando estiver próximo

            if abs(dy) > self.velocidade:
                self.y += self.velocidade if dy > 0 else -self.velocidade
            else:
                self.y = self.target_y  # Corrige para exato quando estiver próximo

            if self.x == self.target_x and self.y == self.target_y:
                self.moving = False  # Finaliza movimento

                    # Verifica se o tempo do efeito de dano passou (1 segundo = 1000 ms)
        if self.dano_timer > 0 and pygame.time.get_ticks() - self.dano_timer > 1000:
            self.cor_atual = self.cor_original  # Retorna à cor normal
            self.dano_timer = 0
    
    def move(self, matrizGrid):
        dir_x, dir_y = self.calcularProximoPasso(matrizGrid)

        if not self.moving:  # Só pode mover se não estiver em movimento
            new_x = self.grid_x + dir_x
            new_y = self.grid_y + dir_y
            
            # Verifica se é um movimento válido dentro dos limites do grid
            if 0 <= new_x < 15 and 0 <= new_y < 17 and matrizGrid[new_y][new_x] == " ":
                matrizGrid[self.grid_y][self.grid_x] = " "  # Libera a célula antiga
                matrizGrid[new_y][new_x] = "Z"  # Ocupa a nova célula
                
                self.grid_x, self.grid_y = new_x, new_y
                self.target_x, self.target_y = new_x * grid_tamanho, new_y * grid_tamanho
                self.moving = True  # Inicia movimento

                if dir_y < 0:
                    self.direction = 'up'
                elif dir_y > 0:
                    self.direction = 'down'
                elif dir_x < 0:
                    self.direction = 'left'
                elif dir_x > 0:
                    self.direction = 'right'


def drawGrass(x, y, variacao):
    camadaChao.blit(spriteGrass, (x, y))
    if variacao == 1:
        camadaChao.blit(spriteGrassWithFlowers, (x, y))

def drawTree(x, y, matriz,rotacao):
    spriteTreeRodar = pygame.transform.rotate(spriteTree, rotacao)
    camadaCharacters.blit(spriteTreeRodar, (x*grid_tamanho, y*grid_tamanho))

def atualizarHUD(player):
    fonte = pygame.font.SysFont("Montserrat", 35)
    texto = fonte.render("Zombie Run", True, (0,0,0))
    tela.blit(texto, [(largura_tela - texto.get_width()) / 2, 5])

    tela.blit(spriteTreeIcon, (0,altura_tela - grid_tamanho * 1.4))
    fonte = pygame.font.SysFont("Montserrat", 22)
    texto = fonte.render(f"{player.getMadeiras()}" , True, (0,0,0))
    tela.blit(texto, [grid_tamanho - 5, altura_tela - 20])

    startHeartX = largura_tela - 50
    startHeartY = altura_tela - 50

    for i in range(0, player.getVida() , 1):
        
        tela.blit(spriteHeart , (startHeartX - 40 * i , startHeartY))
    


def startGame():
    rodando = True
    matrizGrid = []
    matrizGrama = []
    rotacoesTrees = {}
    clicado = False


    # Cria matriz do grid e variação da grama
    for num_linhas in range(0, altura_tela // grid_tamanho):
        linhaMatrizBase = []
        linhaMatrizGrama = []

        for num_colunas in range(0, largura_tela // grid_tamanho):
            linhaMatrizBase.append(" ")
            if random.randint(0, 15) == 4:
                linhaMatrizGrama.append(1)
            else:
                linhaMatrizGrama.append(0)

        matrizGrid.append(linhaMatrizBase)
        matrizGrama.append(linhaMatrizGrama)

    # Spawn de arvores
    for i in range(0,quantidade_trees,1):
        matrizGrid[random.randint(0,16)][random.randint(0,14)] = "#"
        

    player = Player(1, 16)
    matrizGrid[16][1] = 'P'
    zombie = Zombie(1, 1)
    matrizGrid[1][1] = 'Z'
    matrizGrid[8][1] = '#'
    matrizGrid[7][5] = '#'
    vidasArvores = {}






    # Loop principal
    while rodando:
        
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        tela.fill((0, 255, 0))
        tela.blit(camadaChao, (0, 0))
        tela.blit(camadaCharacters, (0, 0))
        camadaCharacters.fill((0, 0, 0, 0))

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
        player.update()
        zombie.move(matrizGrid)
        zombie.update()

        #################################
        ### MECANISMO QUEBRAR ARVORES ###
        #################################
    
        collider_cursor = pygame.Rect(pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1] , 1 ,1)
        pos_cursor = pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1]
        localizaçãoGridX = pos_cursor[0] // 40
        localizaçãoGridY = pos_cursor[1] // 40

        troncos = []
        for y in range(len(matrizGrid)):
            for x in range(len(matrizGrid[y])):
                if matrizGrid[y][x] == '#':
                    retangulo = pygame.draw.rect(camada_transparente, (0,0,255,0), [x * grid_tamanho, y * grid_tamanho, grid_tamanho, grid_tamanho])
                    troncos.append(retangulo)
        #print(troncos)

        
        if not pygame.mouse.get_pressed()[0] and clicado == True:
            clicado = False
                    
        for tronco in troncos:
            if collider_cursor.colliderect(tronco):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if pygame.mouse.get_pressed()[0] and clicado == False and ((localizaçãoGridX - 1 == player.grid_x and localizaçãoGridY == player.grid_y ) or (player.grid_x == localizaçãoGridX + 1 and localizaçãoGridY == player.grid_y) or (localizaçãoGridY - 1 == player.grid_y and localizaçãoGridX == player.grid_x) or (player.grid_y == localizaçãoGridY + 1 and localizaçãoGridX == player.grid_x)):
                    print("break")


                    if not (localizaçãoGridX,localizaçãoGridY) in vidasArvores.keys():
                        vidasArvores[(localizaçãoGridX,localizaçãoGridY)] = 3
                    elif vidasArvores[(localizaçãoGridX,localizaçãoGridY)] > 0:
                        vidasArvores[(localizaçãoGridX,localizaçãoGridY)] = vidasArvores[(localizaçãoGridX,localizaçãoGridY)] - 1
                        rotacoesTrees[(localizaçãoGridX,localizaçãoGridY)] = random.randint(0,360)
                    elif vidasArvores[(localizaçãoGridX,localizaçãoGridY)] <= 0:
                        matrizGrid[localizaçãoGridY][localizaçãoGridX] = " "
                        player.setMadeiras(player.getMadeiras() + 1)

                    print(vidasArvores[(localizaçãoGridX,localizaçãoGridY)])
                    clicado = True

        colliser_zumbi = pygame.draw.rect(camada_transparente, (0,0,255,0), [zombie.grid_x * grid_tamanho, zombie.grid_y * grid_tamanho, grid_tamanho, grid_tamanho])

        if collider_cursor.colliderect(colliser_zumbi):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if player.possuiSword() and random.randint(0,3) == 1 and pygame.mouse.get_pressed()[0] and clicado == False and ((localizaçãoGridX - 1 == player.grid_x and localizaçãoGridY == player.grid_y ) or (player.grid_x == localizaçãoGridX + 1 and localizaçãoGridY == player.grid_y) or (localizaçãoGridY - 1 == player.grid_y and localizaçãoGridX == player.grid_x) or (player.grid_y == localizaçãoGridY + 1 and localizaçãoGridX == player.grid_x)):
                zombie.setVida(zombie.getVida() - 1)

                clicado = True


                
            #################################
            ### MECANISMO DE PEGAR ESPADA ###
            #################################

        if player.getMadeiras() == 7 and not player.possuiSword():
            player.gotSword()
            player.setMadeiras(player.getMadeiras() - 7)

            ##############################
            ### MECANISMO ATAQUE ZUMBI ###
            ##############################
        
        if ((zombie.grid_x - 1 == player.grid_x and zombie.grid_y == player.grid_y ) or (player.grid_x == zombie.grid_x + 1 and zombie.grid_y == player.grid_y) or (zombie.grid_y - 1 == player.grid_y and zombie.grid_x == player.grid_x) or (player.grid_y == zombie.grid_y + 1 and zombie.grid_x == player.grid_x)):

            if random.randint(0,80) == 1:
                player.setVida(player.getVida() -1)

        if player.getVida() == 0:
            return
        if zombie.getVida() == 0:
            print("Ganhou")
            return


        #print(pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1] )











        
        matrizCola = copy.deepcopy(matrizGrid)
        #for t in finder.find(matrizCola):
            #print(t)

        # Draw Grama
        for y in range(len(matrizGrama)):
            for x in range(len(matrizGrama[y])):
                drawGrass(x * grid_tamanho, y * grid_tamanho, matrizGrama[y][x])
        
        # Draw Trees
        for y in range(len(matrizGrid)):
            for x in range(len(matrizGrid[y])):
                if matrizGrid[y][x] == '#':

                    if not (x,y) in rotacoesTrees.keys():
                        rotacoesTrees[(x,y)] = random.randint(0,360)
                    else:
                        drawTree(x , y, matrizGrid, rotacoesTrees[(x,y)])


        
    
        atualizarHUD(player)
        player.draw()
        zombie.draw()
        pygame.display.update()
        clock.tick(60)

    pygame.quit()


while restart:
    startGame()
