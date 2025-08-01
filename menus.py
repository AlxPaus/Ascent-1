import pygame


class View:
  def __init__(self, game, bg_color='grey'):
    self.game = game
    self.bg_color = bg_color
    self.widgets = []

  def update(self):
    for widget in self.widgets:
      widget.update()

  def draw(self):
    self.game.screen.fill(self.bg_color)
    for widget in self.widgets:
      self.game.screen.blit(widget.image, widget.rect)

  def add(self, *widgets):
    self.widgets.extend(widgets)

class Text(pygame.sprite.Sprite):
  def __init__(self, x, y, text, color='black', size=24, anchor='topleft', bg_color:str=None):
    super().__init__()
    self.font = pygame.font.Font('resources/Minecraft.ttf', size)
    if not bg_color:
      self.image = self.font.render(text, True, color)
    else:
      self.image = self.font.render(text, True, color, bg_color)
    kwarg = {anchor:(x, y)}
    self.rect = self.image.get_rect(**kwarg)
    self.text = text
    self.bg_color = bg_color
    self.color = color

  def update(self):
    if not self.bg_color:
      self.image = self.font.render(self.text, True, self.color)
    else:
      self.image = self.font.render(self.text, True, self.color, self.bg_color)
    
    self.rect = self.image.get_rect(center=self.rect.center)

class Button(Text):
  def __init__(self,x,y,text,function,color='white', size=24, anchor='topleft', bg_color:str='gray'):
    super().__init__(x,y,text,color,size,anchor,bg_color)
    self.function = function
    self.active = False
    self.last_mkeys = pygame.mouse.get_pressed(3)

  def update(self):
    m_keys = pygame.mouse.get_pressed(3)
    m_pos = pygame.mouse.get_pos()
    if m_keys[0] and not self.last_mkeys[0] and not self.rect.collidepoint(m_pos):
      self.bg_color = 'gray'
    if m_keys[0] and not self.last_mkeys[0] and self.rect.collidepoint(m_pos):
      self.bg_color = 'black'
      self.function()
    super().update()
    self.last_mkeys = m_keys
  
class Selector(Text):
  def __init__(self,x,y,options,function,color='white', size=24, anchor='topleft', bg_color:str='gray', start_idx=0):
    super().__init__(x,y,'< '+options[start_idx]+' >',color,size,anchor,bg_color)
    self.function = function
    self.bg_color = bg_color
    self.options = options
    self.idx = start_idx
    self.last_keys = pygame.key.get_pressed()
    self.active = False
    
  def update(self):
    m_keys = pygame.mouse.get_pressed(3)
    m_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()
    if not self.active and m_keys[0] and self.rect.collidepoint(m_pos):
      self.active = True
      self.bg_color = 'black'
    if self.active and m_keys[0] and not self.rect.collidepoint(m_pos):
      self.active = False
      self.bg_color = 'gray'
    if self.active:
      if (keys[pygame.K_a] and not self.last_keys[pygame.K_a]) or (keys[pygame.K_d] and not self.last_keys[pygame.K_d]):
        if keys[pygame.K_a] and not self.last_keys[pygame.K_a]:
          self.idx -= 1
          if self.idx < 0:
            self.idx = len(self.options) - 1
        elif keys[pygame.K_d] and not self.last_keys[pygame.K_d]:
          self.idx += 1
          if self.idx >= len(self.options):
            self.idx = 0
        self.text = '< ' + self.options[self.idx] + ' >'
        self.function(self.options[self.idx])
      self.last_keys = keys
    super().update()

