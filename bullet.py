import pygame

class PlayerBullet(pygame.sprite.Sprite):
    def __init__(self, player_rect):
        super().__init__()
        self.image = pygame.Surface([15, 3])
        self.image.fill('BLUE')
        self.rect = self.image.get_rect(center=(player_rect.x + 50, player_rect.y + 50))

    def update(self):
        self.rect.x += VEL
    def get_origin(self):
        return self.origin