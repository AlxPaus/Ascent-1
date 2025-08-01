import config as cfg
from animated_sprite import AnimatedSprite
import pygame
from effect import Effect

import math


class Weapon(AnimatedSprite):

    def __init__(self, game, owner, path, current_ammo=-1, team=0):
        self.owner = owner
        self.path = path
        self.game = game
        x = owner.rect.centerx
        y = owner.rect.centery + cfg.HEIGHT / 20
        name = path.split('/')[-1]
        d = cfg.WEAPONS_CONF[name]
        if 'effect' in d:
            self.effect_name = d['effect']
        else:
            self.effect_name = ''
        ratio = d['ratio']
        self.reload = d['reload']
        self.reload_start = 0

        self.bullet_ratio = d['bullet_ratio']
        self.sound = d['sound']
        self.bullet_speed = d['bullet_speed']
        self.bullet_path = d['bullet_path']
        self.rapidity = d['rapidity']
        self.reloading = False
        if self.game.cheat_mode and owner == self.game.p:
            self.damage = d['damage'] * 20
            self.max_ammo = d['max_ammo'] * 20
            self.rapidity = d['rapidity'] / 5
        else:
            self.damage = d['damage']
            self.max_ammo = d['max_ammo']
            self.rapidity = d['rapidity']
        if current_ammo == -1:
            self.ammo = self.max_ammo
        else:
            self.ammo = current_ammo
        self.bullet_ttl = d['bullet_ttl']
        self.shift = tuple(d['shift'])
        super().__init__(game, x, y, path, ratio)
        self.team = team
        self.image = pygame.transform.flip(self.image, True, True)
        self.angle = 0
        self.orientation = False
        self.last_shot = self.game.time

    def update(self):
        #mx, my = kwargs['mouse_pos']
        self.angle = self.owner.angle  #self.get_angle(mx, my)
        self.rect.centerx = self.owner.rect.centerx
        self.rect.centery = self.owner.rect.centery + cfg.HEIGHT / 20

        if self.orientation and (self.angle <= 90 or self.angle >= 270):
            self.orientation = False
        elif not self.orientation and (90 < self.angle < 270):
            self.orientation = True
        if self.reloading and self.game.time - self.reload_start >= self.reload:

            self.ammo = self.max_ammo
            self.reloading = False

    def shoot(self):
        sprites = self.game.sprites
        bullets = self.game.bullets
        # проверки на скорострельность и тд
        if (self.game.time - self.last_shot >= self.rapidity
                and self.ammo > 0 and not self.reloading):
            if self.team == 0:
                angle = self.get_angle(*self.game.mouse_pos)
            else:
                angle = self.owner.angle
            if not self.effect_name:
                b = Bullet(self.game, self.rect.centerx, self.rect.centery,
                           angle, self.bullet_path, self.damage,
                           self.bullet_speed, self.bullet_ratio, self.team,
                           self, self.bullet_ttl)
            else:
                b = ExplodeBullet(self.game, self.rect.centerx,
                                  self.rect.centery, angle, self.bullet_path,
                                  self.damage, self.bullet_speed,
                                  self.bullet_ratio, self.team, self,
                                  self.bullet_ttl, self.effect_name)
            self.last_shot = self.game.time
            sprites.add(b)
            bullets.add(b)
            self.ammo -= 1
        elif self.ammo <= 0 and not self.reloading:
            self.owner.reload_sound.play()
            self.reloading = True
            self.reload_start = self.game.time


class LyingWeapon(AnimatedSprite):
    pickupsound = pygame.mixer.Sound('resources/sounds/fx_pickup.wav')

    def __init__(self, game, x, y, path, market=False):
        self.x = x
        self.game = game
        self.y = y
        self.floating_dir = True
        self.path = path
        self.dir_time = self.game.time
        name = path.split('/')[-1]
        d = cfg.WEAPONS_CONF[name]
        ratio = d['ratio']
        super().__init__(game, x, y, path, ratio)
        self.game.lying_weapons.add(self)
        if self.path in cfg.LVL0_WEAPONS:
            self.rarity = 0
        elif self.path in cfg.LVL1_WEAPONS:
            self.rarity = 1
        else:
            self.rarity = 2
        self.outline = pygame.mask.from_surface(self.image).outline()
        if market:
            self.price = cfg.lvl_cost[self.rarity] * self.game.levels_completed
        else:
            self.price = 0

    def kill(self):
        self.game.lying_weapons.remove(self)
        super().kill()

    def update(self):
        if self.game.time - self.dir_time >= 240:
            self.floating_dir = not self.floating_dir
            self.dir_time = self.game.time
        c = (self.game.time - self.dir_time) / 240
        h = c * cfg.MEASURE* 0.3
        if not self.floating_dir:
          h = cfg.MEASURE* 0.3 - h
        self.rect.center = self.x, self.y + h

        #key = pygame.key.get_pressed()
        if False and self.rect.colliderect(self.game.p.rect):
            if self.game.p.weapon_dict[1] == None:
                self.game.p.weapon_dict[1] = self.path
                self.game.p.change_weapon(1)
                self.game.p.ammo_left[1] = self.game.p.weapon.max_ammo
            elif self.game.p.weapon_dict[2] == None:
                self.game.p.weapon_dict[2] = self.path
                self.game.p.change_weapon(2)
                self.game.p.ammo_left[2] = self.game.p.weapon.max_ammo
            elif self.game.p.weapon_dict[3] == None:
                self.game.p.weapon_dict[3] = self.path
                self.game.p.change_weapon(3)
                self.game.p.ammo_left[3] = self.game.p.weapon.max_ammo
            else:
                path = self.game.p.weapon_dict[self.game.p.chosen_weapon]
                self.game.p.weapon_dict[self.game.p.chosen_weapon] = self.path
                self.game.p.change_weapon(self.game.p.chosen_weapon)
                nw = LyingWeapon(self.game, self.x, self.y, path)
                self.game.sprites.add(nw)
            self.pickupsound.play()
            self.kill()


class Bullet(AnimatedSprite):

    def __init__(self, game, x, y, angle, path, damage, bullet_speed,
                 bullet_ratio, team, weapon, ttl):
        super().__init__(game, x, y, path, bullet_ratio)
        self.rect.center = (x, y)
        self.pos = [float(x), float(y)]
        self.team = team
        self.weapon = weapon
        self.damage = damage
        self.speed = float(bullet_speed)
        self.birth_time = self.game.time
        self.ttl = ttl
        self.angle = angle
        # self.angle -= 270
        # self.angle = abs(self.angle)
        self.speedx = self.speed * math.cos(math.radians(angle)) * -1
        self.speedy = self.speed * math.sin(math.radians(angle))
        # move bullet relative to direction
        self.rect.move_ip(self.speedx, self.speedy)
                   
        self.angle += 90
        self.shift = (0, 0)
        # key = pygame.key.get_pressed()

    def update(self):
        #super().update()
        self.check_anim_time()
        self.animate()
        #self.rect.move_ip(self.speedx*self.game.delta_time/33, self.speedy*self.game.delta_time/33)
        self.pos[0] += self.speedx * self.game.delta_time / 33
        self.pos[1] += self.speedy * self.game.delta_time / 33
        self.rect.center = self.pos
        # delete if it hits wall
        hits = self.game.blocks.spritecollide(self)
        if hits:
            self.ttl = 0
        # check if it hits entities

        # delete if lives for too long
        if self.game.time - self.birth_time >= self.ttl:
            self.kill()


class ExplodeBullet(Bullet):

    def __init__(self, game, x, y, angle, path, damage, bullet_speed,
                 bullet_ratio, team, weapon, ttl, name):
        super().__init__(game, x, y, angle, path, damage, bullet_speed,
                         bullet_ratio, team, weapon, ttl)
        self._damage = self.damage
        self.damage = 0
        self.effect_name = name

    def explode(self):
        ef = Effect(self.game, self.rect.x, self.rect.y, self.effect_name,
                    self._damage, self.team)
        self.game.sprites.add(ef)
        self.game.bullets.add(ef)
        self.kill()

    def update(self):
        #super().update()
        self.check_anim_time()
        self.animate()
        #self.rect.move_ip(self.speedx*self.game.delta_time/33, self.speedy*self.game.delta_time/33)
        self.pos[0] += self.speedx * self.game.delta_time / 33
        self.pos[1] += self.speedy * self.game.delta_time / 33
        self.rect.center = self.pos
        # delete if it hits wall
        hits = self.game.blocks.spritecollide(self)
        # hits.extend(self.game.entities.spritecollide(self))
        if hits:
            self.ttl = 0

        # delete if lives for too long
        if self.game.time - self.birth_time >= self.ttl:
            self.explode()
            self.kill()
