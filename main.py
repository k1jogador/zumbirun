import pygame
import random
import math

# Inicialização do pygame
pygame.init()
pygame.display.set_caption("Zombie Run")

# Configurações da tela
larguraTela, alturaTela = 600, 700
tela = pygame.display.set_mode((larguraTela, alturaTela))  # tamanho da tela
clock = pygame.time.Clock()

# Player

hitBox = 40
andar = 4
correr = 6


# Cores
preto = (0, 0, 0)
roxo = (128, 0, 128)
verde = (0, 198, 34)
verdeEscuro = (0, 120, 10)
marrom = (141, 73, 37)
vermelho = (255,0,0)

# Classe do Player
class Player:
    def __init__(self, x, y, velocidade):
        self.x = x
        self.y = y
        self.velocidade = velocidade

    def atualizarPlayer(self):
        pygame.draw.rect(tela, preto, [self.x, self.y, hitBox, hitBox])

    def setY(self, y):
        self.y = y

    def getY(self):
        return self.y

    def setX(self, x):
        self.x = x

    def getX(self):
        return self.x

    def setVelocidade(self , velocidade):
        self.velocidade = velocidade


    def getVelocidade(self):
        return self.velocidade

# Classe do Tree
class Tree:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def atualizarTree(self):
        pygame.draw.rect(tela, marrom, [self.x, self.y, hitBox/1.5, hitBox])
        pygame.draw.rect(tela, verdeEscuro, [self.x - ((hitBox - hitBox/1.5)/2), self.y - hitBox * (2/3) , hitBox, hitBox])

    def setY(self, y):
        self.y = y

    def getY(self):
        return self.y

    def setX(self, x):
        self.x = x

    def getX(self):
        return self.x

# inimigo
class Enemy:
    def __init__(self, x, y, velocidade):
        self.rect = pygame.Rect(x, y, hitBox, hitBox)
        self.velocidade = velocidade

    def perseguir(self, player):
        # Calcula a direção até o jogador
        xAlvo = player.getX() - self.rect.x
        yAlvo = player.getY() - self.rect.y
        distancia = math.sqrt(xAlvo**2 + yAlvo**2)  # Distância euclidiana

        # Evita divisão por zero
        if distancia != 0:
            xAlvo = xAlvo / distancia
            yAlvo = yAlvo / distancia

            # Move o inimigo na direção do jogador
            self.rect.x += xAlvo * self.velocidade
            self.rect.y += yAlvo * self.velocidade

    def desenhar(self):
        pygame.draw.rect(tela, vermelho, self.rect)

def desenharHUD():
    fonte = pygame.font.SysFont("Monteserrat", 35)
    texto = fonte.render(f"Zombie Run", True, preto)
    tela.blit(texto, [larguraTela/2 - texto.get_size()[0]/2, 10])

def pode_mover(novo_x, novo_y, trees):
    rect_novo_player = pygame.Rect(novo_x, novo_y, hitBox, hitBox)

    for tree in trees:
        colliserTree = pygame.Rect(tree.getX(), tree.getY(), hitBox / 1.5, hitBox)
        if rect_novo_player.colliderect(colliserTree):
            return False  # Bloqueia movimento se houver colisão

    return True  # Permite movimento se não houver colisão









# Função principal do jogo
def iniciarGame():
    rodando = True

    player = Player(0, 0, 5)
    enemy = Enemy(50, 50, 2)
    trees = []


    while rodando:
        tela.fill(verde)  # Limpa a tela antes de redesenhar
        
        # Detecção de eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                rodando = False

        # Captura teclas pressionadas
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LCTRL]:
            player.setVelocidade(correr)

        if not keys[pygame.K_LCTRL]:
            player.setVelocidade(andar)


        if keys[pygame.K_w] and ((player.getY() - player.getVelocidade() >= 0)) and pode_mover(player.getX(), player.getY() - player.getVelocidade(), trees):
            player.setY(player.getY() - player.getVelocidade())

        if keys[pygame.K_s] and ((player.getY() + player.getVelocidade() <= alturaTela - hitBox)) and pode_mover(player.getX(), player.getY() + player.getVelocidade(), trees):
            player.setY(player.getY() + player.getVelocidade())

        if keys[pygame.K_d] and ((player.getX() + player.getVelocidade() <= larguraTela - hitBox)) and pode_mover(player.getX() + player.getVelocidade(), player.getY(), trees):
            player.setX(player.getX() + player.getVelocidade())

        if keys[pygame.K_a] and ((player.getX() - player.getVelocidade() >= 0)) and pode_mover(player.getX() - player.getVelocidade(), player.getY(), trees):
            player.setX(player.getX() - player.getVelocidade())




        if len(trees) < 20:
            trees.append( Tree( random.randint(0 + 20, larguraTela - 20) , random.randint(50, alturaTela - 25)  ) )






        for tree in trees:
            tree.atualizarTree()


        enemy.perseguir(player)
       # Atualiza o jogador na tela
        enemy.desenhar()
        player.atualizarPlayer()
        desenharHUD()

        # Atualiza a tela
        pygame.display.update()
        clock.tick(24)  # Limita FPS a 60

    pygame.quit()

iniciarGame()
