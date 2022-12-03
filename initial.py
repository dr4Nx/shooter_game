import pygame
import os

pygame.init()

width, height = 1200, 800
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Runner')
FPS = 60
VEL = 4
DEFAULTBULLETVEL = 8
OPPVEL = 2
sswidth, ssheight = 40, 40

main_spaceship_image = pygame.image.load(os.path.join('Assets', 'spaceship_main.png'))
main_spaceship = pygame.transform.rotate(pygame.transform.scale(main_spaceship_image, (sswidth, ssheight)), 270)

opponent_image = pygame.image.load(os.path.join('Assets', 'spaceship_default_opponent.png'))
opponent = pygame.transform.rotate(pygame.transform.scale(opponent_image, (sswidth, ssheight)), 90)

default_background = (50, 50, 50)
border_color = (50, 0, 0)
border = pygame.Rect(900, 0, 2, height)


def draw_window(player_pos, opponent_pos):
    window.fill(default_background)
    pygame.draw.rect(window, border_color, border)
    window.blit(main_spaceship, (player_pos.x, player_pos.y))
    window.blit(opponent, (opponent_pos.x, opponent_pos.y))
    pygame.display.update()


def handle_player(keys_pressed, player_pos):
    if keys_pressed[pygame.K_a] and player_pos.x - VEL > 0:
        player_pos.x -= VEL
    if keys_pressed[pygame.K_d] and player_pos.x + VEL + player_pos.width < 900:
        player_pos.x += VEL
    if keys_pressed[pygame.K_w] and player_pos.y - VEL > 0:
        player_pos.y -= VEL
    if keys_pressed[pygame.K_s] and player_pos.y + VEL + player_pos.height < height:
        player_pos.y += VEL


def handle_default_opponent(opponent_pos, player_pos):
    if opponent_pos.y < player_pos.y:
        opponent_pos.y += OPPVEL
    if opponent_pos.y > player_pos.y:
        opponent_pos.y -= OPPVEL


def main():
    player_pos = pygame.Rect(100, 400, sswidth, ssheight)
    opponent_pos = pygame.Rect(1000, 400, sswidth, ssheight)

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys_pressed = pygame.key.get_pressed()
        handle_player(keys_pressed, player_pos)
        handle_default_opponent(opponent_pos, player_pos)
        draw_window(player_pos, opponent_pos)

    pygame.quit()


if __name__ == "__main__":
    main()
