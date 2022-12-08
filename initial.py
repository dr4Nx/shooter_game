import pygame
import os

pygame.init()

width, height = 1200, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Space Runner')
test_font = pygame.font.Font('Fonts/pixel_font.ttf', 50)
game_font = pygame.font.Font('Fonts/pixel_font.ttf', 10)
FPS = 60
VEL = 4
DEFAULTBULLETVEL = 3
DEFAULTOPPBULLETVEL = 3
OPPVEL = 2
sswidth, ssheight = 30, 30
firerate = 10
oppfirerate = 5
default_background = (50, 50, 50)
border_color = (50, 0, 0)
font_color = (200, 200, 250)
border = pygame.Rect(900, 0, 2, height)

# Title Screen
player_title = pygame.image.load('Assets/spaceship_main.png').convert_alpha()
player_title = pygame.transform.rotozoom(player_title, 270, 2)
player_title_rect = player_title.get_rect(center=(600, 100))

game_message = test_font.render('Press space to begin', False, font_color)
game_message_rect = game_message.get_rect(center=(600, 300))

player = pygame.sprite.GroupSingle()
playerbullets = pygame.sprite.Group()
enemybullets = pygame.sprite.Group()
tempboss = pygame.sprite.GroupSingle()


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.Surface([15, 3])
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect(center=(player_rect.x + 50, player_rect.y + 15))

    def update(self):
        self.rect.x += (width - self.rect.x) / 30 + DEFAULTBULLETVEL
        if self.rect.x > width:
            self.kill()
            if self.alive():
                print("Error")


class StandardEnemyBullet(pygame.sprite.Sprite):
    def __init__(self, origin_rect):
        super().__init__()
        self.image = pygame.Surface([15, 3])
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(origin_rect.x - 20, origin_rect.y + 15))

    def update(self):
        self.rect.x -= DEFAULTOPPBULLETVEL + self.rect.x / 50
        if self.rect.x < 0:
            self.kill()
            if self.alive():
                print("Error")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join(
            'Assets', 'spaceship_main.png')).convert_alpha(), (sswidth, ssheight)), 270)
        self.rect = self.image.get_rect(center=(400, 300))
        self.frames = 0
        self.health = 500

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
        if self.frames % firerate == 0:
            self.fire()
        if self.health <= 0:
            self.kill()


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, origin):
        super().__init__()
        self.image = pygame.Surface([origin.health / 10, 5])


class Boss(pygame.sprite.Sprite):
    def __init__(self, health):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_default_opponent.png')).convert_alpha(),
                                                                    (sswidth, ssheight)), 90)
        self.rect = self.image.get_rect(center=(1100, 300))
        self.health = health
        self.frames = 0

    def fire(self):
        enemybullets.add(StandardEnemyBullet(self.rect))

    def update(self, player_pos):
        if self.rect.y < player_pos.y:
            self.rect.y += OPPVEL
        if self.rect.y > player_pos.y:
            self.rect.y -= OPPVEL
        if self.health <= 0:
            self.kill()
        self.frames += 1
        if self.frames % oppfirerate == 0:
            self.fire()


def draw_border():
    pygame.draw.rect(window, border_color, border)


def detect_player_hits():
    if tempboss.sprite is not None:
        if pygame.sprite.spritecollide(tempboss.sprite, playerbullets, True):
            tempboss.sprite.health -= 10
            return True


def detect_opponent_hits():
    if player.sprite is not None:
        if pygame.sprite.spritecollide(player.sprite, enemybullets, True):
            player.sprite.health -= 10


def check_player_alive():
    if player.sprite is not None:
        return True
    return False


def check_pause():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_ESCAPE]:
        pygame.time.wait(50)
        return True
    return False


def check_unpause():
    keys_pressed = pygame.key.get_pressed()
    if keys_pressed[pygame.K_SPACE]:
        pygame.time.wait(50)
        return False
    return True


def requires_player_alive(wave=1):
    tempboss.update(player.sprite.get_player_rect())
    health_message = game_font.render(f'Health: {player.sprite.health} [Esc] to pause', False,
                                      (255 - player.sprite.health / 2,
                                       375 - max(player.sprite.health / 2,
                                                 255 - player.sprite.health / 2),
                                       player.sprite.health / 2))
    health_message_rect = health_message.get_rect(center=(150, 30))
    window.blit(health_message, health_message_rect)


def main():
    clock = pygame.time.Clock()
    running = True
    game_active = False
    paused = False
    score = 0
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if game_active:
                pass
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    player.empty()
                    tempboss.empty()
                    enemybullets.empty()
                    playerbullets.empty()
                    player.add(Player())
                    tempboss.add(Boss(500))
                    score = 0

        if game_active:
            if paused:
                window.fill(default_background)
                pause_message = test_font.render('Press space to continue', False, font_color)
                pause_message_rect = pause_message.get_rect(center=(600, 300))
                score_message = test_font.render(f'Your current score: {score}', False, font_color)
                score_message_rect = score_message.get_rect(center=(600, 500))
                window.blit(player_title, player_title_rect)
                window.blit(pause_message, pause_message_rect)
                window.blit(score_message, score_message_rect)
                pygame.display.update()
                paused = check_unpause()
            else:
                window.fill(default_background)
                player.draw(window)
                player.update()
                tempboss.draw(window)
                if player.sprite is not None:
                    requires_player_alive()
                playerbullets.draw(window)
                playerbullets.update()
                enemybullets.draw(window)
                enemybullets.update()
                if detect_player_hits():
                    score += 10
                detect_opponent_hits()
                draw_border()
                paused = check_pause()
                # Health

                game_active = check_player_alive()
                pygame.display.update()
        else:
            score_message = test_font.render(f'Your last score: {score}', False, font_color)
            score_message_rect = score_message.get_rect(center=(600, 500))
            window.fill(default_background)
            window.blit(player_title, player_title_rect)
            window.blit(game_message, game_message_rect)
            window.blit(score_message, score_message_rect)
            pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
