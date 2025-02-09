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
spriteZombie = pygame.transform.scale(pygame.image.load("source/mob/zombie.png"), (grid_tamanho, grid_tamanho))
spriteTree = pygame.transform.scale(pygame.image.load("source/tree.png"), (grid_tamanho, grid_tamanho))
spriteTreeIcon = pygame.transform.scale(pygame.image.load("source/treeIcon.png"), (grid_tamanho *1.4, grid_tamanho * 1.4))

class Player:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real (em pixels)
        self.target_x, self.target_y = self.x, self.y  # Destino
        self.velocidade = 5  # Pixels por frame
        self.moving = False  # Indica se o personagem está em movimento
        self.direction = 'down'

        self.madeiras = 0
        self.possuiEspada = False

    def getMadeiras(self):
        return self.madeiras

    def setMadeiras(self, madeiras):
        self.madeiras = madeiras





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
        containerPlayer.fill((0, 0, 0, 0))  # Limpa o container
        
        if self.direction == 'up':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayer, 270)
        elif self.direction == 'down':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayer, 90)
        elif self.direction == 'left':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayer, 0)
        elif self.direction == 'right':
            playerDirecaoCorreta = pygame.transform.rotate(spritePlayer, 180)
        containerPlayer.blit(playerDirecaoCorreta, (0, 0))
        camadaCharacters.blit(containerPlayer, (self.x, self.y))

class Zombie:
    def __init__(self, x, y):
        self.grid_x, self.grid_y = x, y  # Posição no grid
        self.x, self.y = x * grid_tamanho, y * grid_tamanho  # Posição real (em pixels)
        self.target_x, self.target_y = self.x, self.y  # Destino
        self.velocidade = 2  # Pixels por frame
        self.moving = False  # Indica se o personagem está em movimento
        self.direction = 'down'

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

        
        containerZombie.blit(zombieDirecaoCorreta, (0, 0))
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
    texto = fonte.render(f"Madeiras coletadas: {player.getMadeiras()}" , True, (0,0,0))
    tela.blit(texto, [grid_tamanho * 1.4, altura_tela - grid_tamanho * 1.4 * 0.5])

    


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
        if teclasPressionadas[pygame.K_w]:
            player.move(0, -1, matrizGrid)
        if teclasPressionadas[pygame.K_s]:
            player.move(0, 1, matrizGrid)
        if teclasPressionadas[pygame.K_a]:
            player.move(-1, 0, matrizGrid)
        if teclasPressionadas[pygame.K_d]:
            player.move(1, 0, matrizGrid)
        player.update()
        zombie.move(matrizGrid)
        zombie.update()

        #################################
        ### MECANISMO QUEBRAR ARVORES ###
        #################################
    
        collider_cursor = pygame.Rect(pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1] , 1 ,1)
        pos_cursor = pygame.mouse.get_pos()[0] , pygame.mouse.get_pos()[1] 

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
                if pygame.mouse.get_pressed()[0] and clicado == False:
                    print("break")
                    localizaçãoGridX = pos_cursor[0] // 40
                    localizaçãoGridY = pos_cursor[1] // 40

                    if not (localizaçãoGridX,localizaçãoGridY) in vidasArvores.keys():
                        vidasArvores[(localizaçãoGridX,localizaçãoGridY)] = 15
                    elif vidasArvores[(localizaçãoGridX,localizaçãoGridY)] > 0:
                        vidasArvores[(localizaçãoGridX,localizaçãoGridY)] = vidasArvores[(localizaçãoGridX,localizaçãoGridY)] - 1
                        rotacoesTrees[(localizaçãoGridX,localizaçãoGridY)] = random.randint(0,360)
                    elif vidasArvores[(localizaçãoGridX,localizaçãoGridY)] <= 0:
                        matrizGrid[localizaçãoGridY][localizaçãoGridX] = " "
                        player.setMadeiras(player.getMadeiras() + 1)

                    print(vidasArvores[(localizaçãoGridX,localizaçãoGridY)])
                    clicado = True


                



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


startGame()
