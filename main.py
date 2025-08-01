import pygame
import config as cfg
from raycasting import RayCasting
pygame.init()
pygame.mixer.init()
from weapon import ExplodeBullet
from animated_sprite import Group, MasterGroup
from player import Player
from interface import UI
from effect import Effect
import random
from graph import create_level
from room import create_room
from menus import View, Selector, Text, Button

menu_name = 'main' # main game settings
# SDICT = cfg.S_DICT

def reverse_visible(ar):
  visible = ar == 0
  ar[visible] = 155
  visible = ~visible
  ar[visible] = 0


def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)
  
    
class Game: 
  def __init__(self):
    self.clock = pygame.time.Clock()
    self.time = 0
    self.debug_mode = False
    self.size = [cfg.WIDTH, cfg.HEIGHT]
    self.new_lights = cfg.LIGHTS
    if cfg.FULLSCREEN:
      self.screen = pygame.display.set_mode(self.size, pygame.FULLSCREEN)
    else:
      self.screen = pygame.display.set_mode(self.size)
    self.shiftx = cfg.WIDTH * 0.9 # 430
    self.shifty = cfg.HEIGHT * 0.9 # 240    
    self.tmp = []
    self.new_raycast = RayCasting(self)
    self.wallmap = []
    self.sprites = MasterGroup(self)
    self.entities = Group(self)
    self.bullets = Group(self)
    self.blocks = Group(self)
    self.weapons = Group(self)
    self.delta_time = 1
    self.obstacles = []
    self.lying_weapons = Group(self)
    self.door_group = []
    self.levels_completed = 0
    self.cheat_mode = True
    self.cx, self.cy = 0, 0
    self.p = None
    self.ui = None
    self.bg_image = pygame.Surface((46*cfg.MEASURE, 46*cfg.MEASURE))
    pygame.mixer.music.load('resources/music/bgm_defence.wav')
    # pygame.mixer.music.play()

    self.menu_view = View(self)
    self.settings_view = View(self)
    
    
    play_b = Button(150, 100, 'Play', self.to_game, anchor='center')
    quit_b = Button(150,200,'Quit', pygame.quit, anchor = 'center', bg_color = 'grey')
    settings_b = Button(150, 150, 'Settings', self.to_options,anchor = 'center')
    self.menu_view.add( play_b, quit_b,settings_b)
    fps_idx = [30, 45, 60, 120].index(cfg.FPS)
    back_b = Button(100, 50, 'back', self.to_menu_save_settings,anchor = 'center')
    buttons_b = Button(250, 50, 'Buttons', self.to_buttons,anchor = 'center')
    selector1 = Selector(100, 100, ['30', '45', '60', '120'], self.change_fps, start_idx=fps_idx)
    self.fullscreen_b = Button(100, 250, 'Fullscreen ',self.toggle_fullscreen,anchor = 'center')
    if cfg.FULLSCREEN:
      self.fullscreen_b.text += '+'
    else:
      self.fullscreen_b.text += '-'
    
    self.lights_b = Button(100, 150, 'Lights ', self.toggle_light,anchor = 'center')
    if self.new_lights:
      self.lights_b.text += '+'
    else:
      self.lights_b.text += '-'
    

    res_idx = ['480x270', '1440x810', '1600x900', '1920x1080'].index(f'{cfg.WIDTH}x{cfg.HEIGHT}')
    res_selector = Selector(0, 0, ['480x270', '1440x810', '1600x900', '1920x1080'], self.change_res, start_idx=res_idx)
    
    self.buttons_view = View(self)
    w_b = Button(60, 40,f'Up: {chr(cfg.BUTTONS["forward"])}', lambda: self.get_new_button('forward', w_b),anchor = 'center')
    a_b = Button(60, 80, f'Left: {chr(cfg.BUTTONS["left"])}', lambda: self.get_new_button('left', a_b),anchor = 'center')
    s_b = Button(60, 120, f'Back: {chr(cfg.BUTTONS["back"])}', lambda: self.get_new_button('back', s_b) ,anchor = 'center')
    d_b = Button(60, 160, f'Right: {chr(cfg.BUTTONS["right"])}', lambda: self.get_new_button('right', d_b),anchor = 'center')
    to_settings_b = Button(60, 10,'Back', self.to_options,anchor = 'center')
    action_b =  Button(60, 260, f'Action: {chr(cfg.BUTTONS["take_weapon"])}', lambda: self.get_new_button('take_weapon', action_b),anchor = 'center')
    jump_b =  Button(60, 240, f'Jump: {chr(cfg.BUTTONS["jump"])}', lambda: self.get_new_button('jump', action_b),anchor = 'center')
    ability_b =  Button(60, 280, f'Ability: {chr(cfg.BUTTONS["shockwave"])}', lambda: self.get_new_button('shockwave', action_b),anchor = 'center')
    
    self.buttons_view.add(w_b, a_b, s_b, d_b,to_settings_b,action_b,jump_b,ability_b)
   
    self.settings_view.add(selector1,back_b,self.lights_b,res_selector,self.fullscreen_b,buttons_b)
    

  def setup(self):
    self.lying_weapons.empty()
    self.weapons.empty()
    self.sprites.empty()
    self.bullets.empty()
    self.blocks.empty()
    self.wallmap = []
    self.obstacles = []
    self.door_group = []
    self.levels_completed += 1
    if self.p is None:
      self.p = Player(self, 1.3*cfg.MEASURE, 3.3*cfg.MEASURE)
    else:
      self.p.rect.topleft = (1.3*cfg.MEASURE, 3.3*cfg.MEASURE)
    self.sprites.add(self.p)
    self.entities.add(self.p)
    self.ui = UI(self)
    self.recreate_level()
    
  def recreate_level(self):
    doors, content = create_level(3, self.levels_completed)
    for i in range(3):
      for j in range(3):
        n = j + i * 3
        self.door_group.extend(create_room(self, j*(cfg.ROOM_SIZE+2), i*(cfg.ROOM_SIZE+2), doors=doors[n], content_function=content[n]))
    self.bg_image = pygame.Surface((46*cfg.MEASURE, 46*cfg.MEASURE))
    floor_imgs = [
      pygame.image.load(f'resources/floor/f60{i}.png') for i in range(1, 7)]
    floor_imgs = [pygame.transform.scale(img, (cfg.MEASURE, cfg.MEASURE)) for img in floor_imgs]
    for i in range(46):
      for j in range(46):
        img = random.choice(floor_imgs)
        self.bg_image.blit(img, (i*cfg.MEASURE, j*cfg.MEASURE))
        
  def close_doors(self):
    for door in self.door_group:
      door.close()

  def open_doors(self):
    for door in self.door_group:
      door.open()

  def toggle_fullscreen(self):
    cfg.S_DICT['FULLSCREEN'] = not cfg.S_DICT['FULLSCREEN']
    cfg.FULLSCREEN = not cfg.FULLSCREEN
    self.fullscreen_b.text = 'Fullscreen'
    if cfg.FULLSCREEN:
      self.fullscreen_b.text += '+'
    else:
      self.fullscreen_b.text += '-'

  def get_new_button(self, action: str, button:Button):
    start = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start < 10000:
      events = pygame.event.get()
      for event in events:
          if event.type == pygame.QUIT:
              return None
          if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_ESCAPE:
                return None
              else:
                button.text = action.capitalize() + ': ' + chr(event.key)
                cfg.BUTTONS[action] = event.key
                return None
    
    
  def change_fps(self, val2):
    cfg.FPS = int(val2)
    cfg.S_DICT['FPS'] = int(val2)

  def toggle_light(self):
    cfg.S_DICT['LIGHTS'] = not cfg.S_DICT['LIGHTS']
    self.new_lights = not self.new_lights
    self.lights_b.text = 'Lights'
    if self.new_lights:
      self.lights_b.text += '+'
    else:
      self.lights_b.text += '-'
    # self.remake_screen()
    
  def change_res(self, val2):
    cfg.WIDTH, cfg.HEIGHT = map(int, val2.split('x'))
    cfg.S_DICT['WIDTH'], cfg.S_DICT['HEIGHT'] = map(int, val2.split('x'))
    # self.remake_screen()
  
  def to_game(self):
    global menu_name
    menu_name = 'game'

  def to_menu(self):
    global menu_name
    menu_name = 'main'

  def to_buttons(self):
    global menu_name
    menu_name = 'buttons'

  def to_menu_save_settings(self):
    cfg.dump_settings(cfg.S_DICT)
    global menu_name
    menu_name = 'main'

  def to_options(self):
    global menu_name
    menu_name = 'settings'


  def draw(self):
    self.screen.fill((0, 100, 100))
    self.screen.blit(self.bg_image, (self.cx, self.cy))
    self.sprites.draw()
    #self.weapons.draw()
    
    if self.new_lights:
      self.new_raycast.draw()
      
    self.ui.draw()
    
  def update(self):
    self.mkeys = pygame.mouse.get_pressed(3)
    mx, my = pygame.mouse.get_pos()
    self.mouse = (mx, my)
    
    px = self.p.rect.centerx
    py = self.p.rect.centery
    # set camera at center  
    self.cx = self.size[0]//2 - px
    self.cy = self.size[1]//2 - py
    # adjust by mouse position
    self.cx -= 0.8 * (mx - self.size[0]//2)
    self.cy -= 0.8 * (my - self.size[1]//2)

    self.mouse_pos = (mx-self.cx, my-self.cy)
    # collisions
    hits = self.entities.collide(self.bullets)
    for reciever, bullets in hits.items():
      for bullet in bullets:
        if bullet.team != reciever.team and reciever.hp > 0:
          if type(bullet) == ExplodeBullet:
            bullet.explode()
            reciever.recieve_damage(bullet.damage)
          elif type(bullet) != Effect:
            reciever.recieve_damage(bullet.damage)
            bullet.kill()
          elif type(bullet) == Effect:
            if not reciever in bullet.damaged:
              reciever.recieve_damage(bullet.damage)
              bullet.damaged[reciever] = self.time
    self.new_raycast.update()
    self.sprites.update()
    #self.weapons.update()
    self.ui.update()
    
    

  def mainloop(self):
    global menu_name
    run = True
    while run:
        self.delta_time = self.clock.tick(cfg.FPS)
        events = pygame.event.get()
        if menu_name == 'game':
          for event in events:
              if event.type == pygame.QUIT:
                  menu_name = 'main'
              if event.type == pygame.KEYDOWN:
                  if event.key == pygame.K_v:
                    self.debug_mode = not self.debug_mode
                  if event.key == pygame.K_ESCAPE:
                    menu_name = 'main'
          self.update()
          self.draw()
          self.time += self.delta_time
        elif menu_name == 'main':
          self.menu_view.update()
          self.menu_view.draw()
        elif menu_name == 'settings':
          self.settings_view.update()
          self.settings_view.draw()
        elif menu_name == 'buttons':
          self.buttons_view.update()
          self.buttons_view.draw()
        pygame.display.flip()

  
def game_run():
    G = Game()
    G.setup()
    G.mainloop()
    
      
if __name__ == '__main__':
    game_run()
