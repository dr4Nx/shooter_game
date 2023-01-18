import math
import random
import pygame
import os
from numpy.random import randint
import numpy as np

pygame.init()

spawnshipevent = pygame.USEREVENT + 1
width, height = 1200, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('Pandemic Punchout')
test_font = pygame.font.Font('Fonts/pixel_font.ttf', 50)
game_font = pygame.font.Font('Fonts/pixel_font.ttf', 15)
score_font = pygame.font.Font('Fonts/pixel_font.ttf', 20)
FPS = 60
VEL = 4
DEFAULTBULLETVEL = 8
DEFAULTOPPBULLETVEL = 8
OPPVEL = 2
MISSILEVEL = 1
sswidth, ssheight = 40, 40
bosswidth, bossheight = 50, 50
missilewidth, missileheight = 20, 20
playermaxcharge = 250
firerate = 15
defaultdamage = 5
defaultmissiledamage = 20
oppfirerate = 30
default_background = pygame.transform.scale(pygame.image.load('Assets/nonblurred_background.jpg'),
                                            (width, height)).convert_alpha()
blurred_background = pygame.transform.scale(pygame.image.load('Assets/background_blurred.jpg'),
                                            (width, height)).convert_alpha()
border_color = (50, 0, 0)
font_color = (0, 0, 0)
border = pygame.Rect(900, 0, 2, height)
playerhealth = 250
defaultenemyhealth = 15
healthpackspawn = 15

# Title Screen
player_title = pygame.image.load('Assets/doctor.png').convert_alpha()
player_title = pygame.transform.rotozoom(player_title, 0, 0.25)

player_title_rect = player_title.get_rect(center=(600, 100))

game_message = test_font.render('Press space to begin', False, font_color)
game_message_rect = game_message.get_rect(center=(600, 300))

player = pygame.sprite.GroupSingle()
firebar = pygame.sprite.GroupSingle()
playerbullets = pygame.sprite.Group()
enemybullets = pygame.sprite.Group()
tempboss = pygame.sprite.GroupSingle()
enemies = pygame.sprite.Group()
healthbars = pygame.sprite.Group()
backgroundbars = pygame.sprite.Group()
enemymissiles = pygame.sprite.Group()
healthpacks = pygame.sprite.Group()


class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'syringe.png')).convert_alpha(),
                                   (25, 10))
        self.rect = self.image.get_rect(center=(player_rect.x + 50, player_rect.y + 15))

    def update(self):
        self.rect.x += DEFAULTBULLETVEL
        if self.rect.x > width:
            self.kill()
            if self.alive():
                print("Error")


class StandardEnemyBullet(pygame.sprite.Sprite):
    def __init__(self, origin_rect):
        super().__init__()
        self.image = pygame.Surface([15, 3])
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(origin_rect.x - 20, origin_rect.y + origin_rect.height / 2))

    def update(self):
        self.rect.x -= DEFAULTOPPBULLETVEL
        if self.rect.x < 0:
            self.kill()
            if self.alive():
                print("Error")


class TargetedEnemyBullet(pygame.sprite.Sprite):
    def __init__(self, origin_rect, target_point):
        super().__init__()
        self.image = pygame.Surface([10, 10])
        self.image.fill((255, 100, 100))
        self.rect = self.image.get_rect(center=(origin_rect.x - 15, origin_rect.centery))
        self.target = target_point
        self.distx = target_point.x - self.rect.x
        self.disty = target_point.y - self.rect.y
        self.totalvel = MISSILEVEL + 8
        self.xvel = np.round(
            self.totalvel * (self.distx + 1) / (abs(self.distx) + abs(self.disty) + 1)) + random.choice(
            [1, 0, 0, 0, 0, -1])
        self.yvel = np.round(
            self.totalvel * (self.disty + 1) / (abs(self.distx) + abs(self.disty) + 1)) + random.choice(
            [1, 0, 0, 0, 0, -1])
        self.frames = 0

    def update(self):
        self.rect.x += self.xvel
        self.rect.y += self.yvel
        if self.rect.x < 0:
            self.kill()
            if self.alive():
                print("Error")


class HealthPack(pygame.sprite.Sprite):
    def __init__(self, rect):
        super().__init__()
        self.image = pygame.transform.rotate(
            pygame.transform.scale(pygame.image.load(os.path.join('Assets', 'healthpack.png')).convert_alpha(),
                                   (missilewidth, missileheight)), 90)
        self.rect = self.image.get_rect(center=(rect.centerx, rect.centery))

    def update(self):
        self.rect.x -= OPPVEL
        if self.rect.x < 0:
            self.kill()


class EnemyMissile(pygame.sprite.Sprite):
    def __init__(self, origin_rect):
        super().__init__()
        self.image = self.image = pygame.transform.scale(pygame.image.load(os.path.join(
            'Assets', 'idlemissile.png')).convert_alpha(), (missilewidth, missileheight))
        self.rect = self.image.get_rect(center=(origin_rect.centerx, origin_rect.centery))
        self.moves = 0
        self.distx = 0
        self.disty = 0
        self.totalvel = MISSILEVEL
        self.xvel = 0
        self.yvel = random.choice([2, 4, -2, -4])
        self.frames = 0

    def rotate(self, player_loc):
        self.distx = player_loc.x - self.rect.x
        self.disty = player_loc.y - self.rect.y
        self.xvel = np.round(self.totalvel * (self.distx + 1) / (abs(self.distx) + abs(self.disty) + 1))
        self.yvel = np.round(self.totalvel * (self.disty + 1) / (abs(self.distx) + abs(self.disty) + 1))

    def move(self):
        self.rect.x += self.xvel
        self.rect.y += self.yvel

    def update(self, player_loc):
        self.frames += 1
        if self.frames % 5 == 0 and self.frames > 20 and self.totalvel < 6:
            self.totalvel += 0.5
            self.xvel -= 0.5
        if 50 < self.frames < 200:
            self.image = self.image = pygame.transform.scale(pygame.image.load(os.path.join(
                'Assets', 'activemissile.png')).convert_alpha(), (missilewidth, missileheight))
            self.rotate(player_loc)
        else:
            self.image = self.image = pygame.transform.scale(pygame.image.load(os.path.join(
                'Assets', 'idlemissile.png')).convert_alpha(), (missilewidth, missileheight))
        self.move()
        if self.frames > 500:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.scale(pygame.image.load(os.path.join(
            'Assets', 'doctor.png')).convert_alpha(), (sswidth, ssheight))
        self.rect = self.image.get_rect(center=(400, 300))
        self.frames = 0
        self.radius = 15
        self.health = playerhealth
        self.originalhealth = playerhealth
        self.chargebar = playermaxcharge
        self.maxcharge = playermaxcharge
        self.chargeframes = 120
        self.truefire = firerate

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

    def handle_firebar(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_SPACE] and self.chargebar > 0:
            self.chargeframes = 0
            self.truefire = math.floor(firerate / 3)
            self.chargebar -= 1
        elif self.chargeframes < 120:
            self.chargeframes += 1
            self.truefire = firerate
        else:
            if self.chargebar < playermaxcharge:
                self.chargebar += 1
            self.truefire = firerate

    def get_player_rect(self):
        return self.rect

    def fire(self):
        playerbullets.add(PlayerBullet(self.rect))

    def update(self):
        self.handle_player()
        self.handle_firebar()
        self.frames += 1
        if self.frames % self.truefire == 0:
            self.fire()
        if self.health <= 0:
            self.kill()


class SuperFireBar(pygame.sprite.Sprite):
    def __init__(self, origin):
        super().__init__()
        self.origin = origin
        self.image = pygame.Surface([self.origin.chargebar * 200 / self.origin.maxcharge, 20])
        self.image.fill((100, 100, 255))
        self.rect = self.image.get_rect(
            topleft=(50, height - 200))

    def update(self):
        self.image = pygame.Surface([self.origin.chargebar * 200 / self.origin.maxcharge, 20])
        if self.origin.maxcharge == self.origin.chargebar:
            self.image.fill((255, 255, 100))
        elif self.origin.chargeframes >= 120:
            self.image.fill((0, 255, 255))
        elif self.origin.chargebar < self.origin.maxcharge // 3:
            self.image.fill((255, 0, 0))
        else:
            self.image.fill((100, 100, 255))

        self.rect = self.image.get_rect(
            topleft=(50, height - 100))


class PlayerHealthBar(pygame.sprite.Sprite):
    def __init__(self, origin):
        super().__init__()
        self.origin = origin
        self.originalhealth = self.origin.health
        try:
            self.originalhealth = self.origin.originalhealth
        except AttributeError:
            pass

        self.image = pygame.Surface([self.origin.health * 200 / self.originalhealth, 20])
        self.image.fill(
            (255 - self.origin.health * 255 / self.originalhealth, 255 * self.origin.health / self.originalhealth, 0))
        self.rect = self.image.get_rect(
            topleft=(50, height - 50))

    def update(self):
        if self.origin.health <= 0:
            self.kill()
        if self.rect.centerx <= 15:
            self.kill()
        else:
            self.image = pygame.Surface([self.origin.health * 200 / self.originalhealth, 20])
            self.image.fill((255 - self.origin.health * 255 / self.originalhealth,
                             255 * self.origin.health / self.originalhealth, 0))
            self.rect = self.image.get_rect(
                topleft=(50, height - 50))


class HealthBar(pygame.sprite.Sprite):
    def __init__(self, origin):
        super().__init__()
        self.origin = origin
        self.originalhealth = self.origin.health
        try:
            self.originalhealth = self.origin.originalhealth
        except AttributeError:
            pass

        self.image = pygame.Surface([self.origin.health * 80 / self.originalhealth, 5])
        self.image.fill(
            (255 - self.origin.health * 255 / self.originalhealth, 255 * self.origin.health / self.originalhealth, 0))
        self.rect = self.image.get_rect(
            center=(self.origin.rect.x + self.origin.rect.width / 2, self.origin.rect.y - 10))

    def update(self):
        if self.origin.health <= 0:
            self.kill()
        if self.rect.centerx <= 25:
            self.kill()
        else:
            self.image = pygame.Surface([self.origin.health * 80 / self.originalhealth, 5])
            self.image.fill((255 - self.origin.health * 255 / self.originalhealth,
                             255 * self.origin.health / self.originalhealth, 0))
            self.rect = self.image.get_rect(
                center=(self.origin.rect.x + self.origin.rect.width / 2, self.origin.rect.y - 10))


class EnemyDefault(pygame.sprite.Sprite):
    def __init__(self, health, truefirerate, startingy):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_default_opponent.png')).convert_alpha(),
                                                                    (sswidth, ssheight)), 90)
        self.rect = self.image.get_rect(center=(width, startingy))
        self.health = health
        self.originalhealth = health
        self.frames = 0
        self.firerate = truefirerate * random.choice([0.5, 1, 1.5, 2, 2, 2, 2, 2.5, 3, 3.5, 4, 4.5, 5])
        self.speed = random.choice([1, 2, 3])

    def fire(self):
        enemybullets.add(StandardEnemyBullet(self.rect))

    def update(self, player_pos):
        if self.frames < 50 or self.frames > 600:
            self.rect.x -= self.speed
        if self.frames % self.firerate == 0:
            self.fire()
        if self.health <= 0:
            self.kill()
            randnum = np.random.randint(low=1, high=healthpackspawn)
            if randnum == 2:
                healthpacks.add(HealthPack(self.rect))
        if self.rect.x < 0:
            self.kill()
        self.frames += 1


class EnemyDefaultMissile(pygame.sprite.Sprite):
    def __init__(self, health, truefirerate, startingy):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_missile.png')).convert_alpha(),
                                                                    (sswidth, ssheight)), 90)
        self.rect = self.image.get_rect(center=(width, startingy))
        self.health = health
        self.originalhealth = health

        self.frames = 0
        self.speed = random.choice([1, 2, 3])
        self.firerate = truefirerate * 2 * random.choice([3, 3.5, 4, 4.5, 5])

    def fire(self):
        enemymissiles.add(EnemyMissile(self.rect))

    def update(self, player_pos):
        if self.frames < 50 or self.frames > 600:
            self.rect.x -= self.speed
        if self.frames % self.firerate < 20 and self.frames % 10 == 0:
            self.fire()
        if self.health <= 0:
            self.kill()
            randnum = np.random.randint(low=1, high=healthpackspawn)
            if randnum == 2:
                healthpacks.add(HealthPack(self.rect))

        if self.rect.x < 0:
            self.kill()
        self.frames += 1


class EnemyTargeted(pygame.sprite.Sprite):
    def __init__(self, health, truefirerate, startingy):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_focused.png')).convert_alpha(),
                                                                    (sswidth, ssheight)), 0)
        self.rect = self.image.get_rect(center=(width, startingy))
        self.health = health
        self.originalhealth = health

        self.frames = 0
        self.firerate = truefirerate
        self.speed = random.choice([1, 2, 3])

    def fire(self):
        enemybullets.add(TargetedEnemyBullet(self.rect, player.sprite.rect))

    def update(self, player_pos):
        if self.frames < 50 or self.frames > 600:
            self.rect.x -= self.speed
        if self.frames % self.firerate <= 40 and self.frames % 10 == 0:
            self.fire()
        if self.health <= 0:
            self.kill()
            randnum = np.random.randint(low=1, high=healthpackspawn)
            if randnum == 2:
                healthpacks.add(HealthPack(self.rect))
        if self.rect.x < 0:
            self.kill()
        self.frames += 1


class Boss(pygame.sprite.Sprite):
    def __init__(self, health, truefirerate):
        super().__init__()
        self.image = pygame.transform.rotate(pygame.transform.scale(pygame.image.load(os.path.join('Assets',
                                                                                                   'spaceship_default_opponent.png')).convert_alpha(),
                                                                    (bosswidth, bossheight)), 90)
        self.rect = self.image.get_rect(center=(1100, 300))
        self.health = health
        self.frames = 0
        self.firerate = truefirerate
        self.missilefirerate = 15 * truefirerate
        healthpacks.add(HealthPack(self.rect))

    def fire(self):
        enemybullets.add(StandardEnemyBullet(self.rect))

    def missilefire(self):
        enemymissiles.add(EnemyMissile(self.rect))
        enemybullets.add(TargetedEnemyBullet(self.rect, player.sprite.rect))

    def update(self, player_pos):
        if self.rect.y < player_pos.y:
            self.rect.y += OPPVEL
        if self.rect.y > player_pos.y:
            self.rect.y -= OPPVEL
        if self.health <= 0:
            healthpacks.add(HealthPack(self.rect))
            healthpacks.add(HealthPack(self.rect))
            healthpacks.add(HealthPack(self.rect))
            self.kill()

        self.frames += 1
        if self.frames % self.firerate == 0:
            self.fire()
        if self.frames % self.missilefirerate <= 30 + self.missilefirerate / 3 and self.frames % 10 == 0:
            self.missilefire()


class BlankBackgroundA(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([200, 20])
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect(topleft=[50, height - 50])


class BlankBackgroundB(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([200, 20])
        self.image.fill((50, 50, 50))
        self.rect = self.image.get_rect(topleft=[50, height - 100])


def newwave(wave):
    pygame.time.set_timer(spawnshipevent, 328, wave % 13)


def spawnship(location, wave):
    choices = [EnemyDefault(defaultenemyhealth + 5 * (wave // 13), oppfirerate - 2 * (wave // 13), location),
               EnemyDefault(defaultenemyhealth + 5 * (wave // 13), oppfirerate - 2 * (wave // 13), location),
               EnemyDefault(defaultenemyhealth + 5 * (wave // 13), oppfirerate - 2 * (wave // 13), location),
               EnemyDefaultMissile(defaultenemyhealth + 10 * (wave // 13), oppfirerate - 2 * (wave // 13),
                                   location),
               EnemyTargeted(defaultenemyhealth, oppfirerate * 8, location)]
    enemies.add(random.choice(choices))


def newboss(wave):
    enemies.add(Boss(300 + 100 * (wave // 13), max(oppfirerate - 2 * (wave // 13), 1)))
    for sprite in enemies:
        healthbars.add(HealthBar(sprite))


def draw_border():
    pygame.draw.rect(window, border_color, border)


def detect_player_hits():
    collisions = pygame.sprite.groupcollide(enemies, playerbullets, False, True)
    for enemy in collisions:
        enemy.health -= 5
        return True
    if pygame.sprite.groupcollide(player, enemies, True, True):
        pass


def detect_opponent_hits():
    if player.sprite is not None:
        if pygame.sprite.spritecollide(player.sprite, enemybullets, True):
            player.sprite.health -= defaultdamage
        if pygame.sprite.spritecollide(player.sprite, enemymissiles, True):
            player.sprite.health -= defaultmissiledamage


def detect_health_packs():
    if player.sprite is not None:
        if pygame.sprite.spritecollide(player.sprite, healthpacks, True):
            player.sprite.health = min(playerhealth, player.sprite.health + 50)


def detect_missile_collision():
    if pygame.sprite.groupcollide(playerbullets, enemymissiles, True, True):
        pass


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


def requires_player_alive(wave, score):
    enemies.update(player.sprite.get_player_rect())
    enemymissiles.update(player.sprite.get_player_rect())
    healthbars.update()

    wave_message = score_font.render(
        f'Wave: {wave}', False,
        font_color)
    wave_message_rect = wave_message.get_rect(center=(150, 50))
    score_message = score_font.render(f'Score: {score}', False, font_color)
    score_message_rect = score_message.get_rect(center=(width - 150, 50))
    health_message = game_font.render(
        f'HP: {player.sprite.health}/{player.sprite.originalhealth}', False, font_color
    )
    health_message_rect = health_message.get_rect(topleft=(50, height - 75))
    super_fire_message = game_font.render(
        f'Energy: {player.sprite.chargebar}/{player.sprite.maxcharge}', False, font_color
    )
    super_fire_rect = super_fire_message.get_rect(topleft=(50, height - 125))
    if wave == 1:
        instructions_message = game_font.render(
            '[Esc] to Pause, [Space] to use energy/shoot faster', False, (0, 0, 255)
        )
        instructions_rect = instructions_message.get_rect(center=(width/2, 150))
        window.blit(instructions_message, instructions_rect)
    window.blit(health_message, health_message_rect)
    window.blit(wave_message, wave_message_rect)
    window.blit(score_message, score_message_rect)
    window.blit(super_fire_message, super_fire_rect)


def main():
    clock = pygame.time.Clock()
    running = True
    game_active = False
    paused = False
    score = 0
    wave = 0
    initialclock = 0
    templocs = [20, 60, 100, 140, 180, 220, 260, 300, 340, 380, 420, 460, 500, 540, 580]
    backgroundbars.add(BlankBackgroundA())
    backgroundbars.add(BlankBackgroundB())
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == spawnshipevent:
                initialclock = pygame.time.get_ticks()
                location = random.choice(templocs)
                spawnship(location, wave)
                templocs.remove(location)
                healthbars.empty()
                for sprite in enemies:
                    healthbars.add(HealthBar(sprite))
                if player.sprite is not None:
                    healthbars.add(PlayerHealthBar(player.sprite))

            if game_active:
                pass
            else:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    initialclock = pygame.time.get_ticks()
                    game_active = True
                    player.empty()
                    firebar.empty()
                    enemies.empty()
                    enemybullets.empty()
                    enemymissiles.empty()
                    playerbullets.empty()
                    healthbars.empty()
                    healthpacks.empty()
                    player.add(Player())
                    firebar.add(SuperFireBar(player.sprite))
                    newwave(1)
                    healthbars.add(PlayerHealthBar(player.sprite))
                    score = 0
                    wave = 1

        if game_active:
            if paused:
                window.blit(blurred_background, (0, 0))
                pause_message = test_font.render('Press space to continue', False, font_color)
                pause_message_rect = pause_message.get_rect(center=(600, 300))
                score_message = test_font.render(f'Score: {score}', False, font_color)
                score_message_rect = score_message.get_rect(center=(600, 500))
                window.blit(player_title, player_title_rect)
                window.blit(pause_message, pause_message_rect)
                window.blit(score_message, score_message_rect)
                pygame.display.update()
                paused = check_unpause()
            else:
                window.blit(default_background, (0, 0))
                enemybullets.update()
                healthpacks.update()
                player.update()
                firebar.update()
                playerbullets.update()

                player.draw(window)
                enemies.draw(window)
                if player.sprite is not None:
                    requires_player_alive(wave, score)
                if len(enemies.sprites()) == 0 and pygame.time.get_ticks() > initialclock + 500:
                    score += wave * 20
                    wave += 1
                    if wave % 13 == 0:
                        newboss(wave)
                    else:
                        initialclock = pygame.time.get_ticks()
                        templocs = [20, 60, 100, 140, 180, 220, 260, 300, 340, 380, 420, 460, 500, 540, 580]
                        newwave(wave)

                playerbullets.draw(window)
                enemybullets.draw(window)
                enemymissiles.draw(window)
                healthpacks.draw(window)
                backgroundbars.draw(window)
                firebar.draw(window)
                healthbars.draw(window)

                if detect_player_hits():
                    score += defaultdamage
                detect_opponent_hits()
                detect_missile_collision()
                detect_health_packs()
                draw_border()
                paused = check_pause()
                # Health
                game_active = check_player_alive()
                pygame.display.update()
        else:
            score_message = test_font.render(f'Score: {score}', False, font_color)
            score_message_rect = score_message.get_rect(center=(600, 500))
            window.blit(blurred_background, (0, 0))
            window.blit(player_title, player_title_rect)
            window.blit(game_message, game_message_rect)
            window.blit(score_message, score_message_rect)
            pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
