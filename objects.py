import pygame
from animated_sprite import AnimatedSprite
import random
import config as cfg
from weapon import LyingWeapon


class ChestLid(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type, position, scale):
        super().__init__()

        if (type == 0):
            if (position == 'left'):
                self.image = pygame.image.load('resources/chests/blue_chest/open/left.png')
            else:
                self.image = pygame.image.load('resources/chests/blue_chest/open/right.png')
        elif (type == 1):
            if (position == 'left'):
                self.image = pygame.image.load('resources/chests/blue_chest/open/left.png')
            else:
                self.image = pygame.image.load('resources/chests/blue_chest/open/right.png')
        else:
            if (position == 'left'):
                self.image = pygame.image.load('resources/chests/blue_chest/open/left.png')
            else:
                self.image = pygame.image.load('resources/chests/blue_chest/open/right.png')
        w, h = int(self.image.get_size()[0] * scale), int(self.image.get_size()[1] * scale)
        self.image = pygame.transform.scale(self.image, (w, h))
        self.rect = self.image.get_rect()
        if position == 'left':
            self.rect.right = x
        else:
            self.rect.left = x
        self.rect.top = y
        self.speedx = 0
        self.game = game

    def update(self):
        self.rect.move_ip(self.speedx * self.game.delta_time / 33, 0)


class Chest(pygame.sprite.Sprite):
    def __init__(self, game, x, y, type):
        self.game = game
        super().__init__()
        if (type == 0):
            self.image = pygame.image.load('resources/chests/blue_chest/0.png')
            scale = cfg.MEASURE / self.image.get_size()[0]
            w, h = int(self.image.get_size()[0] * scale), int(self.image.get_size()[1] * scale)
            self.image = pygame.transform.scale(self.image, (w, h))
            self.body = pygame.image.load('resources/chests/blue_chest/open/body.png')
            self.body = pygame.transform.scale(self.body, (w, h))
        elif (type == 1):
            self.image = pygame.image.load('resources/chests/blue_chest/0.png')
            scale = cfg.MEASURE / self.image.get_size()[0]
            w, h = int(self.image.get_size()[0] * scale), int(self.image.get_size()[1] * scale)
            self.image = pygame.transform.scale(self.image, (w, h))
            self.body = pygame.image.load('resources/chests/blue_chest/open/body.png')
            self.body = pygame.transform.scale(self.body, (w, h))
        else:
            self.image = pygame.image.load('resources/chests/blue_chest/0.png')
            scale = cfg.MEASURE / self.image.get_size()[0]
            w, h = int(self.image.get_size()[0] * scale), int(self.image.get_size()[1] * scale)
            self.image = pygame.transform.scale(self.image, (w, h))
            self.body = pygame.image.load('resources/chests/blue_chest/open/body.png')
            self.body = pygame.transform.scale(self.body, (w, h))

        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = type
        self.startx = -1
        self.frame = 0
        self.l_lid = ChestLid(game, self.rect.centerx, self.rect.top, type, 'left', scale)
        self.r_lid = ChestLid(game, self.rect.centerx, self.rect.top, type, 'right', scale)
        self.spawned_weapon = False

        self.outline = pygame.mask.from_surface(self.image).outline()
    def open(self):
        self.game.lying_weapons.remove(self)
        self.startx = self.r_lid.rect.centerx
        self.image = self.body
        self.l_lid.speedx = -2
        self.r_lid.speedx = 2
        self.game.sprites.add(self.l_lid)
        self.game.sprites.add(self.r_lid)
        

    def update(self):
        if not self.spawned_weapon and self.startx != -1 and abs(self.startx - self.r_lid.rect.centerx) >= self.r_lid.rect.width:
            self.r_lid.rect.left = self.rect.right
            self.l_lid.rect.right = self.rect.left
            self.r_lid.speedx = 0
            self.l_lid.speedx = 0
            if (self.type == 0):
              
              path = random.choice(cfg.LVL0_WEAPONS)
              lw = LyingWeapon(self.game, self.rect.centerx, self.rect.centery, path)
              self.game.sprites.add(lw)
            
            elif (self.type == 1):
                path = random.choice(cfg.LVL1_WEAPONS)
                lw = LyingWeapon(self.game, self.rect.centerx, self.rect.centery, path)
                self.game.sprites.add(lw)
                
            elif (self.type == 2):
                path = random.choice(cfg.LVL2_WEAPONS)
                lw = LyingWeapon(self.game, self.rect.centerx, self.rect.centery, path)
                self.game.sprites.add(lw)
                
            self.spawned_weapon = True
class Merchant(AnimatedSprite):
  def __init__(self,game,x,y):
    super().__init__(game, x, y,'resources/merchant',cfg.PLAYER_SCALE*1.2,anim_speed = cfg.ANIM_SPEED/2)
  def update(self):
        super().update()

class Portal(AnimatedSprite):
    def __init__(self, game, x, y):
        self.game = game
        game.lying_weapons.add(self)
        self.teleported = False
        super().__init__(game, x, y,'resources/portal',cfg.PLAYER_SCALE*3)
        #self.anim_name = 'idle'
    def update(self):
        super().update()
    def teleport(self):
      if not self.teleported:
        print('teleported')
        self.game.setup()
        #self.teleported = True
        
class Potion(AnimatedSprite):
  def __init__(self,game,x,y,type):
    self.game = game
    self.type = type
    self.x,self.y = x,y
    if self.type == "small_heal":
      self.rarity = 0
      self.path = "resources/potions/small_heal"
    elif self.type == "medium_heal":
      self.rarity = 1
      self.path = "resources/potions/medium_heal"
    super().__init__(game,x,y,self.path,ratio = cfg.PLAYER_SCALE/4)
    self.dir_time = pygame.time.get_ticks()
    self.floating_dir = True
    self.outline = pygame.mask.from_surface(self.image).outline()
    self.game.lying_weapons.add(self)
    self.price = cfg.lvl_cost[self.rarity] * self.game.levels_completed
   
    
  def take_potion(self):
    if self.type == 'small_heal':
      self.game.p.hp += cfg.PLAYER_HP/4
      self.game.p.hp = min(self.game.p.hp, cfg.PLAYER_HP)
      self.kill()
      self.game.lying_weapons.remove(self) 
    elif self.type == 'medium_heal':
      self.game.p.hp += cfg.PLAYER_HP/2
      self.game.p.hp = min(self.game.p.hp,cfg.PLAYER_HP)
      self.kill()
      self.game.lying_weapons.remove(self)
      
  def update(self):
      if self.game.time - self.dir_time >= 240:
          self.floating_dir = not self.floating_dir
          self.dir_time = self.game.time
      c = (self.game.time - self.dir_time) / 240
      h = c * cfg.MEASURE* 0.3
      if not self.floating_dir:
          h = cfg.MEASURE* 0.3 - h
      self.rect.center = self.x, self.y + h