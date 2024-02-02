import sys
import os
from typing import Any

from pygame import *
from random import randint

win_width, win_height = 700, 500
window = display.set_mode((win_width, win_height))
display.set_caption("Shooter 2D")

clock = time.Clock()

fps = 60  # ? 1 секунда = 60 тиков
game_run = True
game_finished = False

# ! Створення звуків
mixer.init()
mixer.music.load("space.ogg")
mixer.music.play()
mixer.music.set_volume(0.025)

fire_sound = mixer.Sound("laser.mp3")
fire_sound.set_volume(0.025)

player_hit = mixer.Sound("player_hit.mp3")
player_hit.set_volume(0.05)

enemy_destroy = mixer.Sound("enemy_hit.mp3")
enemy_destroy.set_volume(0.05)
# ! Створення шрифтів
font.init()
stats_font = font.SysFont("Arial", 32)
main_font = font.SysFont('serif', 72)
hp_font = font.SysFont("Arial", 18)

# ! Створюю текст поразки та перемоги
win_text = main_font.render("You win!", True, (50, 200, 0))
lose_text = main_font.render("You lose!", True, (200, 50, 0))


class GameSprite(sprite.Sprite):
    def __init__(self, img, x, y, w, h, speed):
        super().__init__()

        self.image = transform.smoothscale(
            image.load(img),
            (w, h)
        )

        self.speed = speed

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))


class Player(GameSprite):
    fire_delay = fps * 0.1
    fire_timer = fire_delay
    can_fire = True
    health = 5

    def update(self):
        
        hp_txt = hp_font.render(f"HP: {self.health}", True, (0, 200, 25))

        if not self.can_fire:
            if self.fire_timer > 0:
                self.fire_timer -= 1
            else:
                self.fire_timer = self.fire_delay
                self.can_fire = True

        keys = key.get_pressed()
        if keys[K_a] or keys[K_LEFT]:
            if self.rect.x > 0:
                self.rect.x -= self.speed
        if keys[K_d] or keys[K_RIGHT]:
            if self.rect.x < win_width - self.image.get_width():
                self.rect.x += self.speed
        if keys[K_SPACE]:
            if self.can_fire:
                self.fire()
                self.can_fire = False
                
        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y - 25))

    def fire(self):
        new_bullet = Bullet("bullet.png", self.rect.centerx -
                            7.5, self.rect.y + 10, 15, 25, 15)
        bullet_group.add(new_bullet)
        fire_sound.play()


class Enemy(GameSprite):
    health = randint(1, 3)
    
    def update(self):
        global lost
        
        hp_txt = hp_font.render(f"HP: {self.health + 1}", True, (200, 200, 200))

        if self.rect.y >= win_height: # ! Якщо торкнувся нижньої границі
            lost += 1
            self.kill()
        elif sprite.collide_rect(self, player): # ! Якщо торкнувся гравця
            player.health -= 1
            player_hit.play()
            self.kill()
        else: # ! Якщо просто летить
            self.rect.y += self.speed
        
        window.blit(hp_txt, (self.rect.x + self.image.get_width() / 2 - hp_txt.get_width() / 2, self.rect.y - 25))
            
class Asteroid(GameSprite):
    def update(self):
        if self.rect.y >= win_height: # ! Якщо торкнувся нижньої границі
            self.kill()
        elif sprite.collide_rect(self, player): # ! Якщо торкнувся гравця
            player.health -= 1
            self.kill()
        else: # ! Якщо просто летить
            self.rect.y += self.speed

class Bullet(GameSprite):
    def update(self):
        global kills

        if self.rect.y <= 0:
            self.kill()
            
        enemy = sprite.spritecollide(self, enemys_group, False) # ! Список ворогів, з якими зіткнулись

        if enemy: # ! Якщо зіткнулись з ворогом
            enemy = enemy[0] # ! Отримуємо ворога, з яким зіткнулись
            if enemy.health <= 0: # ! Якщо у ворога нема ХП
                kills += 1
                enemy_destroy.play()
                enemy.kill()
            else: # ! Якщо у ворога є ХП
                enemy.health -= 1
            self.kill() # ! В будь якому разі виділяємо кулю

        self.rect.y -= self.speed


# ! Для таймера спавна ворогів
enemy_respawn_delay = fps * 0.75  # ? між спавном ворогів чекаємо 2 секунди
enemy_respawn_timer = enemy_respawn_delay  # ? таймер

# ! Для таймера спавна астероїдів
asteroid_respawn_delay = fps * 2.25  # ? між спавном ворогів чекаємо 2 секунди
asteroid_respawn_timer = asteroid_respawn_delay  # ? таймер

# ! Змінні для лічильників
lost, kills = 0, 0

# ! Створення спрайтів
background = GameSprite("space.jpg", 0, 0, win_width, win_height, 0)
player = Player("korabl.png", win_width / 2, win_height - 100, 70, 90, 6)

# ! Створення груп спрайтів
enemys_group = sprite.Group()
bullet_group = sprite.Group()
asteroid_group = sprite.Group()

while game_run:

    for ev in event.get():
        if ev.type == QUIT:
            game_run = False

    if not game_finished:

        kills_text = stats_font.render(
            f"Рахунок: {kills}/25", True, (220, 220, 220))
        lost_text = stats_font.render(
            f"Пропущено: {lost}/8", True, (220, 220, 220))

        # ! Спавн ворогів
        if enemy_respawn_timer > 0:
            enemy_respawn_timer -= 1
        else:
            new_enemy = Enemy("ufo.png", randint(
                0, win_width - 72), -72, 72, 64, randint(2, 5))
            new_enemy.health = randint(0, 2)
            enemys_group.add(new_enemy)
            enemy_respawn_timer = enemy_respawn_delay
        
        # ! Спавн астероїдів
        if asteroid_respawn_timer > 0:
            asteroid_respawn_timer -= 1
        else:
            new_asteroid = Asteroid("asteroid.png", randint(
                0, win_width - 72), -72, randint(72, 102), randint(64, 94), randint(2, 5))
            asteroid_group.add(new_asteroid)
            asteroid_respawn_timer = asteroid_respawn_delay

        background.reset()

        player.reset()
        enemys_group.draw(window)
        bullet_group.draw(window)
        asteroid_group.draw(window)

        player.update()
        enemys_group.update()
        bullet_group.update()
        asteroid_group.update()

        window.blit(kills_text, (5, 5))
        window.blit(lost_text, (5, 38))

        # ! Умови кінця гри
        if kills >= 25:
            background.reset()
            window.blit(win_text, (win_width / 2 - win_text.get_width() / 2, win_height / 2 - win_text.get_height() / 2))
            game_finished = True

        if lost >= 8 or player.health <= 0:
            background.reset()
            window.blit(lose_text, (win_width / 2 - lose_text.get_width() /
                        2, win_height / 2 - lose_text.get_height() / 2))
            game_finished = True

        display.update()

    clock.tick(fps)
