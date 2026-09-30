import pygame

pygame.init()
screen = pygame.display.set_mode((600, 600))

background = pygame.image.load("background.jpeg")
background = pygame.transform.scale(background, (600, 600))


def draw_stickman(surface):
    black = (0, 0, 0)
    pygame.draw.circle(surface, black, (300, 200), 30, 3)       # kafa
    pygame.draw.line(surface, black, (300, 230), (300, 350), 3)  # govde
    pygame.draw.line(surface, black, (300, 260), (250, 310), 3)  # sol kol
    pygame.draw.line(surface, black, (300, 260), (350, 310), 3)  # sag kol
    pygame.draw.line(surface, black, (300, 350), (260, 430), 3)  # sol bacak
    pygame.draw.line(surface, black, (300, 350), (340, 430), 3)  # sag bacak


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))
    draw_stickman(screen)
    pygame.display.flip()

pygame.quit()