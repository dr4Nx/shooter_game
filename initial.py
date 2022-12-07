import pygame
import os

pygame.init()

width, height = 1200, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Runner')
FPS = 60
VEL = 4
DEFAULTBULLETVEL = 20
OPPVEL = 2
sswidth, ssheight = 30, 30


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.Surface([15, 3])
        self.image.fill('BLUE')
        self.rect = self.image.get_rect(center=(player_rect.x + 50, player_rect.y + 15))

    def update(self):
        self.rect.x += DEFAULTBULLETVEL
        if self.rect.x > width:
            self.kill()
            if self.alive():
                print("Error")


default_background = (50, 50, 50)
border_color = (50, 0, 0)
border = pygame.Rect(900, 0, 2, height)

player = pygame.sprite.GroupSingle()
playerbullets = pygame.sprite.Group()
tempboss = pygame.sprite.GroupSingle()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join(
            'Assets', 'spaceship_main.png')).convert_alpha(), (sswidth, ssheight)), 270)
        self.rect = self.image.get_rect(center=(450, 300))
        self.frames = 0

    def handle_player(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a] and self.rect.x - VEL > 0:
            self.rect.x -= VEL
        if keys_pressed[pygame.K_d] and self.rect.x + VEL + self.rect.width < 900:
            self.rect.x += VEL
        if keys_pressed[pygame.K_w] and self.rect.y - VEL > 0:
            self.rect.y -= VEL
        if keys_pressed[pygame.K_s] and self.rect.y + VEL + self.rect.height < height:
            self.rect.y += VEL

    def get_player_rect(self):
        return self.rect

    def fire(self):
        playerbullets.add(PlayerBullet(self.rect))

    def update(self):
        self.handle_player()
        self.frames += 1
        if self.frames % 10 == 0:
            self.fire()


class Boss(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_default_opponent.png')).convert_alpha(),
                                                                    (sswidth, ssheight)), 90)
        self.rect = self.image.get_rect(center=(1000, 300))

    def update(self, player_pos):
        if self.rect.y < player_pos.y:
            self.rect.y += OPPVEL
        if self.rect.y > player_pos.y:
            self.rect.y -= OPPVEL


def draw_border():
    pygame.draw.rect(window, border_color, border)


def handle_default_opponent(opponent_pos, player_pos):
    if opponent_pos.y < player_pos.y:
        opponent_pos.y += OPPVEL
    if opponent_pos.y > player_pos.y:
        opponent_pos.y -= OPPVEL


frames = 0


def main():
    player.add(Player())
    tempboss.add(Boss())
    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        window.fill(default_background)

        player.draw(window)
        player.update()
        tempboss.draw(window)
        tempboss.update(player.sprite.get_player_rect())
        playerbullets.draw(window)
        playerbullets.update()
        draw_border()
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
