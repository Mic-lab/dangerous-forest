'''
To do/idea list

- menu fade after play
- settings getting behind game
- fix half vector half pixel art frame
- 800x450 resolution not working

- img property decorator
- Enemys and player order
- Removing stage attribute and storing in stage list
- Optimize enemy images (every instance of a enemy uses the same animation, rip ram)
- Composition > inhertience
- Not load all enemys at once, more stable ram
- When render_end_screen(loose=True) called, the borders are hidden for a frame
'''

import pygame
from pygame.locals import *
import sys
import webbrowser
import time
from random import choice
from math import ceil, floor, sqrt
from data.scripts.config import *

debug = True

# Initilize ------------------------------------------------------------------------------------- #
pygame.init()
clock = pygame.time.Clock()
FPS = 60
monitor_size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
if debug:
    monitor_size = 1280, 720
    #monitor_size = 800, 450
canvas = pygame.Surface((640, 360))
if debug:
    screen = pygame.display.set_mode(monitor_size)
else:
    screen = pygame.display.set_mode(monitor_size, pygame.FULLSCREEN)
pygame.display.set_caption('Dangerous forest')

def update_load(text):
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    screen.blit(pygame.transform.scale(canvas, monitor_size), (0, 0))
    text_img = get_font(64).render(text + '...', True, (240, 240, 240))
    screen.blit(text_img, (monitor_size[0]*0.5 - text_img.get_width()*0.5, monitor_size[1]*0.5 - text_img.get_height()*0.5))
    pygame.display.update()

def get_font(size):
    return pygame.font.Font('data/img/font.ttf', size)

update_load('Initializing')

RESIZE_SCALE = int(screen.get_width() / canvas.get_width())

class Cursor:
    path = 'data/img/cursor/'

    def __init__(self, mode, colorkey, scale=1):
        self.mode = mode
        self.colorkey = colorkey
        self.scale =  scale
        
    def render(self, surface, pos, offset):
        img = pygame.image.load(f'{Cursor.path}{self.mode}.png').convert()
        img.set_colorkey(self.colorkey)
        surface.blit(pygame.transform.scale(img, (img.get_width()*self.scale,
                                                  img.get_height()*self.scale)),
                                                  [pos[0] + offset[0],
                                                  pos[1] + offset[1]])

class Button:
    text_distance = [0, 0]
    fill_distance = 3
    
    # Since text in the middlek of the button the distance
    text_distance = (text_distance[0]*2, text_distance[1] * 2)
     
    def __init__(self, pos, size, font, text, colors=((80, 150, 180), (60, 90, 120), (200, 200, 200), (100, 190, 200), (80, 130, 140), (255, 255, 255), (130, 210, 250), (110, 160, 190), (255, 255, 150))):
        """
        colors[n]
        
        0: fill   unselected
        1: border unselected
        2: text   unselected
        3: fill   selected
        4: border selected
        5: text   selected
        6: fill   clicked
        7: border clicked
        8: text   clicked
        """

        self.pos = pos
        self.size = size
        self.font = font
        self.text = text
        self.colors = colors
        self.selected = False
        self.del_sel = False     # Delayed at start
        self.del_sel_frame = 0
        self.clicked = False
        self.del_clicked = False # Delayed at end
        self.clicked_frame = 0
        self.clicked_frame_s = 0
        self.released = False

        # You shouldn't manually change size and text size variables since this condition will only be called on __init__
        # This can be prevented with property decorator, but it isn't really needed 
        if self.size == None:
            self.size = (self.text_obj.get_width() + Button.text_distance[0], self.text_obj.get_height() + Button.text_distance[1])
            
        ##                if self.text_obj.get_width() > self.size[0] - Button.text_distance[0] or self.text_obj.get_height() > self.size[1] - Button.text_distance[1]:
        ##                    raise Exception(f'Button text size must be smaller then button by at least {Button.text_distance} px')
    @property
    def text_obj(self):
        if self.clicked:    return self.font.render('< ' + self.text + ' >', True, self.colors[8])
        elif self.selected: return self.font.render('< ' + self.text + ' >', True, self.colors[5]) 
        else:               return self.font.render(self.text, True, self.colors[2])

    def reset(self):
        self.selected = False
        self.del_sel = False     
        self.del_sel_frame = 0
        self.clicked = False
        self.del_clicked = False 
        self.clicked_frame = 0
        self.clicked_frame_s = 0
        self.released = False

    def update(self, clicked, mouse_down, sound=True):
        self.released = False
        
        if (pygame.mouse.get_pos()[0] > self.pos[0] and pygame.mouse.get_pos()[0] < self.pos[0] + self.size[0]) and (pygame.mouse.get_pos()[1] > self.pos[1] and pygame.mouse.get_pos()[1] < self.pos[1] + self.size[1]):
            self.selected = True
            if clicked: 
                self.clicked = True
            if not mouse_down:
                self.clicked = False
        else:
            self.selected = False
            self.clicked = False

        if not self.selected:
            self.del_sel_frame = 0
            self.del_sel = False
        else:
            if self.del_sel_frame == 1:
                self.del_sel = True

        # Audio and additional updates
        if self.del_sel == False and self.selected:
            if sound:
                
                # IMPLEMENT SOUND
                sounds['select'].play()
            self.del_sel_frame += 1
            if self.del_sel_frame > 2:
                self.del_sel_frame = 2

        if self.clicked:
            self.clicked_frame += 1
            if self.clicked_frame > 2:
                self.clicked_frame = 2
        else:
            if self.clicked_frame != 0:
                if (pygame.mouse.get_pos()[0] > self.pos[0] and pygame.mouse.get_pos()[0] < self.pos[0] + self.size[0]) and (pygame.mouse.get_pos()[1] > self.pos[1] and pygame.mouse.get_pos()[1] < self.pos[1] + self.size[1]):
                    if sound:
                        
                        # IMPLEMENT SOUND
                        sounds['click'].play()
                    self.released = True

            self.clicked_frame = 0

        # the frame it's clicked
        if self.clicked and clicked:
            pass
                
    def render(self, surface):
        if self.selected:
            if self.clicked:
                shift = 6
            else:
                shift = 3
        else:   
            shift = 0

        #pygame.draw.rect(surface, self.colors[1 + shift], (self.pos[0], self.pos[1], self.size[0], self.size[1]))
        #pygame.draw.rect(surface, self.colors[shift], (self.pos[0] + Button.fill_distance, self.pos[1] + Button.fill_distance, self.size[0] - Button.fill_distance*2, self.size[1] - Button.fill_distance*2))
        surface.blit(self.text_obj, (self.pos[0] + self.size[0]/2 - self.text_obj.get_width()/2, self.pos[1] + self.size[1]/2 - self.text_obj.get_height()/2))

class Creature:
    
    def __init__(self, pos, vel, friction, hp, dmg, animations, action, flip, stage):
        self.pos = pos
        self.vel = vel
        self.friction = friction
        self.hp_max = hp
        self._hp = self.hp_max
        self.dmg = dmg
        self.animations = animations
        self.animation_frame = 0
        self.game_animation_frame = 0
        self.flip = flip
        self.stage = stage
        self._action = action
        self.action_switch = True
        self.alive = True
        self.health_bar = None
        self.attacking = False
        self.back_attack = False
        self.update_rect()

    def show_stats(self):
        print('-------------------- Stats --------------------')
        print(f'Instance {self}')
        print(f'Stage    {self.stage}')
        print(f'Pos      {self.pos}')
        print(f'HP max   {self.hp_max}')
        print(f'HP       {self.hp}')
        print(f'DMG      {self.dmg}')
        print('-----------------------------------------------')
        
    def get_health_bar(self, hp_bar_pos, hp_bar_size, color_basic, color_dmg):       
        self.health_bar = Health_bar(hp_bar_pos, hp_bar_size, color_basic, color_dmg)
        
    @property
    def hp(self):
        return self._hp
    
    @property
    def action(self):
        return self._action
        
    @hp.setter
    def hp(self, value):
        if value > self.hp_max:
            self._hp = self.hp_max
        elif value <= 0:
            
            self._hp = 0
            self.alive = False
        else:
            self._hp = value

    @action.setter
    def action(self, value):
        if value != self._action and self.action_switch:
            self._action = value
            self.animation_frame = 0
            self.game_animation_frame = 0
            self.update_rect()

    # Repetition
    def get_rect(self, img):
        x, y, width, height = img.get_bounding_rect()
        return pygame.Rect(x + self.pos[0], y + self.pos[1], width, height)

    def update_rect(self):
        x, y, width, height = pygame.transform.flip(self.animations[self.action][self.animation_frame][1], self.flip[0], self.flip[1]).get_bounding_rect()
        self.rect = pygame.Rect(x + self.pos[0], y + self.pos[1], width, height)
        
    def go_to(self, dest):
        for i in range(2):
            distance = dest[i] - self.pos[i]
            if distance > 0:
                self.vel[i] = sqrt(abs(2*distance*self.friction))
            if distance < 0:
                self.vel[i] = -sqrt(abs(2*distance*self.friction))
                                        
    def attack(self, creature):
        self.attacking = True
        self.attacked_creature = creature
        
        data = pygame.transform.flip(self.animations[self.action][self.animation_frame][1], self.flip[0], self.flip[1]).get_bounding_rect()
        if self.rect.x < creature.rect.x:
            self.flip[0] = False
            self.go_to([creature.pos[0] - ((self.rect.x - self.pos[0]) - (creature.rect.x - creature.pos[0])) - self.rect.width, self.pos[1]])
        else:
            self.flip[0] = True
            creature_img = creature.animations[creature.action][creature.animation_frame][1]
            self_img = self.animations[self.action][self.animation_frame][1]
            distance = (self.rect.x - (creature.rect.x + creature.rect.width))
            self.go_to([self.pos[0] - distance, self.pos[1]])
            
        # Distance traveled in form of velocity
        self.traveled_vel = self.vel.copy()
                
    def update(self):
        if self.stage == stage or self.stage is None:
            attack_animation_reset = False
            output = [False, False]
            # Mouvement ------------------------------------------------------------------------------ #
            for i in range(2):
                self.pos[i] += self.vel[i]
                
                if self.vel[i] > 0:
                    if self.vel[i] - self.friction < 0:
                        self.vel[i] = 0
                    else:
                        self.vel[i] -= self.friction
                elif self.vel[i] < 0:
                    if self.vel[i] + self.friction > 0:
                        self.vel[i] = 0
                    else:
                        self.vel[i] += self.friction

                self.vel[i] = int(self.vel[i])

            # Animation ------------------------------------------------------------------------------ #
            # Make sure to update after rendering or else frame #0 won't show
            
            if not self.alive:
                try:
                    self.animations['death']
                    self.action = 'death'
                except KeyError:
                    # print('[TODO] Add death animation')
                    self.alive = False
                    
                    
                self.action_switch = False

            if not(self.action == 'death' and self.animation_frame == len(self.animations[self.action]) - 1 and self.game_animation_frame == self.animations[self.action][self.animation_frame][0] - 1):
                self.game_animation_frame += 1
                if self.game_animation_frame == self.animations[self.action][self.animation_frame][0]:
                    self.game_animation_frame = 0
                    self.animation_frame += 1
                    if self.animation_frame == len(self.animations[self.action]):
                        self.animation_frame = 0
                        if self.action == 'take hit':
                            self.action = 'idle'
                        if self.action == 'attack':
                            attack_animation_reset = True
                        output[0] = True
            else:
                output[0] = True

            # rect ----------------------------------------------------------------------------------- #
            self.update_rect()
            
            # Attack --------------------------------------------------------------------------------- #
            if self.attacking:
                
                if self.vel[0] == 0:
                    self.action = 'attack'
                    # When the attack animation is finish
                    if attack_animation_reset:
                        self.attacking = False
                        self.attacked_creature = None
                        self.action = 'idle'
                        self.vel[0] = -self.traveled_vel[0]
                        self.back_attack = True

            if self.action == 'attack':
                if self.animation_frame == self.hit_frame and self.game_animation_frame == 0:
                    
                    # Hit frame ---------------------------------------------------------------------- #
                    sounds['hit'].play()
                    if 'take hit' in self.attacked_creature.animations:
                        self.attacked_creature.action = 'take hit'                        
                    else:
                        print('[TODO] add take hit action')

                    self.attacked_creature.hp -= self.dmg

            if self.vel[0] == 0:
                if self.back_attack:
                    output[1] = True
                    self.back_attack = False

            return output

    def render_health_bar(self):
        self.health_bar.render(canvas, self.hp, self.hp_max)

    def render(self, surface):
        if stage == self.stage or self.stage is None:
            if self.health_bar: 
                self.render_health_bar()

            img = self.animations[self.action][self.animation_frame][1]
            #pygame.draw.rect(surface, (255, 255, 255), self.rect, width=1)
            surface.blit(pygame.transform.flip(img, self.flip[0], self.flip[1]), (self.pos))

class Standard_creature(Creature):
    def __init__(self, pos, vel, friction, lvl, xp_max, hp, dmg, animations, action, hit_frame, flip, stage):
        super().__init__(pos, vel, friction, hp, dmg, animations, action, flip, stage)
        
        self._lvl = lvl
        self.OG_XP_MAX = xp_max
        self.xp_max = self.OG_XP_MAX + self.adjust_with_lvl()
        self._xp = 0
        
        self.OG_HP_MAX = hp
        self.hp_max = self.OG_HP_MAX + self.adjust_with_lvl()
        self._hp = self.hp_max
        self.OG_DMG = dmg
        self.dmg = self.OG_DMG + self.adjust_with_lvl()
        
        self.hit_frame = hit_frame
        
    def show_stats(self):
        print('-------------------- Stats --------------------')
        print(f'Instance {self}')
        print(f'Stage    {self.stage}')
        print(f'Pos      {self.pos}')
        print(f'lvl      {self.lvl}')
        print(f'XP max   {self.xp_max}')
        print(f'XP       {self.xp}')
        print(f'HP max   {self.hp_max}')
        print(f'HP       {self.hp}')
        print(f'DMG      {self.dmg}')
        print(f'Action   {self.action}')
        print(f'Frame    {self.animation_frame}')
        print('-----------------------------------------------')
        
    @property
    def lvl(self):
        return self._lvl

    @property
    def xp(self):
        return self._xp

    @property
    def hp(self):
        return self._hp
    
    @hp.setter
    def hp(self, value):
        if value > self.hp_max:
            self._hp = self.hp_max
        elif value <= 0:
            self._hp = 0
            self.alive = False
        else:
            self._hp = value

    @lvl.setter
    def lvl(self, value):
        print(f'lvl has been set to {value}')
        self._lvl = value
        # There's a bit of repetition in the __init__
        self.xp_max = self.OG_XP_MAX + self.adjust_with_lvl()
        self.hp_max = self.OG_HP_MAX + self.adjust_with_lvl()
        self.dmg = self.OG_DMG + self.adjust_with_lvl()

    @xp.setter
    def xp(self, value):
        print(f'xp has been set to {value}')
        self._xp = value
        while self._xp > self.xp_max:
            self._xp -= self.xp_max
            self.lvl += 1
            
    def adjust_with_lvl(self):
        return self.lvl ** 2 * 0.2

class Player(Standard_creature):
    def __init__(self, pos, vel, friction, action, flip):
        super().__init__(pos, vel, friction, 0, 10, 100, 10, load_player(['idle', 'attack', 'take hit', 'death'], [[20, 7, 7, 7], [8, 20, 5, 5], [10, 10, 10], [32, 12, 12, 12, 12, 50]], 3), action, 2, flip, None) 
        self.get_health_bar((25, 40), (400, 15), (62, 158, 81), (250, 250, 250))
        self.inventory = []
        
class Enemy(Standard_creature):
    
    # xp_max, hp, dmg, hit_frame
    STATS = {'goblin': (10, 20, 10, 6),
             'eye': (10, 10, 10, 6),
             'mushroom': (15, 20, 15, 7),
             'skeleton': (1, 50, 20, 6)}
    
    def __init__(self, pos, vel, friction, lvl, flip, TYPE, stage):
        self.TYPE = TYPE
        path = f'data/img/enemy/{self.TYPE}/'

        custom_animations = []
        if self.TYPE == 'goblin':
            custom_animations = [['run'], 
                                 [f'{path}Run.png'], 
                                 [[7, 7, 7, 7, 7, 7, 7, 7]]]
            
        # Animations in common with every TYPE
        animations = [['attack',
                       'death',
                       'idle',
                       'take hit'],
                      
                      [f'{path}Attack.png',
                       f'{path}Death.png',
                       f'{path}Idle.png',
                       f'{path}Take Hit.png'],
                      
                      [[7, 7, 7, 7, 7, 7, 7, 7],
                       [10, 10, 10, 20],
                       [7, 7, 7, 7, 7, 7, 7, 7],
                       [7, 7, 7, 7]]]

        if custom_animations:
            for i in range(len(custom_animations[0])):
                for j in range(3):
                    animations[j].append(custom_animations[j][i])
                
        super().__init__(pos, vel, friction, lvl, Enemy.STATS[self.TYPE][0], Enemy.STATS[self.TYPE][1], Enemy.STATS[self.TYPE][2],
                         load_spritesheet(animations[0], animations[1], [150, 150], (0, 0, 0), animations[2], 2), 'idle', Enemy.STATS[self.TYPE][3], flip, stage)

        self.get_health_bar(self.pos, [60, 8], (200, 50, 50), (200, 100, 100))

    def render_health_bar(self):
        basic_img = pygame.transform.flip(self.animations['idle'][0][1], self.flip[0], self.flip[1])
        rect = self.get_rect(basic_img)
        self.health_bar.pos = [rect.x + rect.width/2 - self.health_bar.size[0]/2, rect.y - 10]
        self.health_bar.render(canvas, self.hp, self.hp_max)

class Boss(Creature):
    STATS = {}
    def __init__(self, pos, vel, friction, hp, dmg, animations, action, flip, stage):
        self.TYPE = TYPE
        super.__init__(pos, vel, friction, hp, dmg, animations, action, flip, stage)
        self.get_health_bar((30, 50), (300, 50), (240, 50, 50), (240, 240, 240))

class Health_bar:
    # BUG: sometimes there's a gap between the white damage taken indicataor surfaces. Theory for cause: rounding. Solution: dont know
    def __init__(self, pos, size, color_basic, color_dmg):
        self.pos = pos
        # Size includes outline
        self.size = size
        self.color_basic = color_basic
        self.color_dmg = color_dmg
        self.rects = []

    # TODO: add update and render method
        
    def render(self, surface, hp, hp_max):
        if not hasattr(self, 'last_hp'):
            self.last_hp = hp
            
        if self.last_hp > hp:
            hp_lost = pygame.Surface([(self.last_hp-hp)/hp_max*self.size[0], self.size[1]-2])
            hp_lost.fill((250, 250, 250))
            hp_lost.set_alpha(255)
            self.rects.append({'surface': hp_lost, 'pos': [self.pos[0] + 1 + hp/hp_max * (self.size[0] - 2), self.pos[1] + 1]})
        
        pygame.draw.rect(surface, (230, 230, 230), [self.pos[0], self.pos[1], self.size[0], self.size[1]])
        pygame.draw.rect(surface, (30, 30, 30), [self.pos[0] + 1, self.pos[1] + 1, self.size[0] - 2, self.size[1] - 2])
        
        i = 0
        while i < len(self.rects):
            if self.rects[i]['surface'].get_alpha() <= 0:
                self.rects.pop(i)
            else:
                self.rects[i]['surface'].set_alpha(self.rects[i]['surface'].get_alpha()-10)   
                surface.blit(self.rects[i]['surface'], self.rects[i]['pos'])
                self.rects[i]['pos'][1] += 1
                i += 1    
        
        pygame.draw.rect(surface, self.color_basic, [self.pos[0] + 1, self.pos[1] + 1, hp/hp_max * (self.size[0] - 2), self.size[1] - 2])
        self.last_hp = hp

class Basic_object:
    # Creature could've inherited from this class, maybe...

    def __init__(self, pos, img):
        self.pos = pos
        self.offset = [0, 0]
        self.img = img

    def render(self, surface):
        surface.blit(self.img, [self.pos[0] + self.offset[0], self.pos[1] + self.offset[1]])
        
def update_cursor():
    if right_down:
        cursor.mode = 'click'
    else:
        cursor.mode = 'normal'
    
    cursor.render(screen, (mx, my), (0, 0))

def update_menu_buttons(mode_):
    # Awful code
    global show_menu
    global mode
    global run
    
    if mode_ == 'menu':
        
        buttons['menu']['play'].text = 'Play'
        buttons['menu']['play'].size = (buttons['menu']['play'].font.render(buttons['menu']['play'].text, True, (0, 0, 0)).get_width() + Button.text_distance[0], buttons['menu']['play'].text_obj.get_height() + Button.text_distance[1])
        button_positions = [(monitor_size[0]/2 - get_font(menu_font_size).render('Play', True, (0, 0, 0)).get_width()/2, monitor_size[1]*0.5),
                            (monitor_size[0]/2 - get_font(menu_font_size).render('Settings', True, (0, 0, 0)).get_width()/2, monitor_size[1]*0.6),
                            (monitor_size[0]/2 - get_font(menu_font_size).render('Quit', True, (0, 0, 0)).get_width()/2, monitor_size[1]*0.7)]
        
    if mode_ == 'play':
        buttons['menu']['play'].text = 'Continue'
        buttons['menu']['play'].size = (buttons['menu']['play'].font.render(buttons['menu']['play'].text, True, (0, 0, 0)).get_width() + Button.text_distance[0], buttons['menu']['play'].text_obj.get_height() + Button.text_distance[1])
        button_positions = [(monitor_size[0]*0.06, monitor_size[1]*0.05),
                            (monitor_size[0]*0.06, monitor_size[1]*0.25),
                            (monitor_size[0]*0.06, monitor_size[1]*0.35)]
        
    for key in buttons['menu']:
        if mode_ == 'menu':
            
            if key == 'back menu':
                continue

        button = buttons['menu'][key]
        
        if key == 'play':
            button.pos = button_positions[0]
            if button.released:
                show_menu = False
                if mode_ == 'menu':
                    mode = 'play'
                elif mode_ == 'play':
                    show_menu = False

        elif key == 'settings':
            button.pos = button_positions[1]
            if button.released:
                show_menu = False
                webbrowser.open('https://www.google.com/search?q=settings&oq=settings&aqs=chrome.0.69i59j69i60.744j0j1&sourceid=chrome&ie=UTF-8')
                
        elif key == 'quit':
            button.pos = button_positions[2]
            if button.released:
                show_menu = False
                run = False

        elif key == 'back menu': 
            if button.released:
                show_menu = False
                mode = 'menu'

        button.update(clicked, right_down)
        button.render(screen)

def load_enemys(map_, load=True):
    global last_stage
    with open(map_) as f:
        data = f.read()
        
    enemys = []

    l = 0
    for line in data.split('\n'):
        if not(line.strip() == '' or line[0].strip() == '#'):
            l += 1

    try:
        i = 0
        for stage in data.split('\n'):
            if not(stage.strip() == '' or stage[0].strip() == '#'):
                if load:
                    update_load(f'Loading stage {i + 1}/{l}')
                ememy_count_total = 0
                enemy_count_current = 0
                for j, enemy in enumerate(stage.split(',')):
                    for k in range(int(enemy.split(' ')[0])):
                        ememy_count_total += 1
                for j, enemy in enumerate(stage.split(',')):
                    for k in range(int(enemy.split(' ')[0])):
                        enemy_count_current += 1
                        enemys.append(Enemy([120 + 300/(ememy_count_total+1)*(enemy_count_current), 100], [0, 0], 1, int(enemy.split(' ')[2]), [True, False], enemy.split(' ')[1], i+1))
                i += 1

    except Exception:
        run_error_screen('Make sure that the map.txt file has the proper format')


    last_stage = max(enemy.stage for enemy in enemys)
    return enemys

def render_end_screen(loose=True):
    global mode
    
    show_borders(canvas.get_height()/2, 10)

    if borders_y == canvas.get_height()/2:
        if loose:
            mode = 'play again?'
        else:
            mode = 'win'

def show_borders(y_max, change_rate=5):
    global borders_y
    
    borders_y += (y_max - borders_y)/change_rate
    if borders_y < y_max + 1 and borders_y > y_max:
        borders_y = y_max
    elif borders_y > y_max - 1 and borders_y < y_max:
        borders_y = y_max
    pygame.draw.rect(canvas, (37, 32, 52), (0, 0, canvas.get_width(), borders_y))
    pygame.draw.rect(canvas, (37, 32, 52), (0, 360 - borders_y, canvas.get_width(), ceil(borders_y)))
    canvas.blit(images['top border'], (0, borders_y))
    canvas.blit(images['bottom border'], (0, 360 - borders_y - images['bottom border'].get_height()))

def initialize_vars():
    global mode
    global stage
    global borders_y
    global borders_y_desired
    global player
    global enemys
    global attack_turn
    global current_death_frame
    global win
    
    mode = 'menu'
    stage = 1
    borders_y = 0
    borders_y_desired = 0
    player = Player([0, 193], [0, 0], 1, 'idle', [False, False])
    enemys = load_enemys('map.txt', load=False)
    attack_turn = 'player'
    current_death_frame = 0
    restart_text.alpha = 0
    continue_text.alpha = 0
    win = False

def run_error_screen(message):
    img = get_font(int(screen.get_width()*0.05)).render(message, True, (240, 240, 240))
    
    while True:

        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        screen.blit(img, get_center_pos(screen, img))

        pygame.display.update()
        clock.tick(30)

cursor = Cursor('normal', (255, 255, 255), 2)

borders_y = 0
borders_y_desired = 0

stage = 1

player = Player([0, 193], [0, 0], 1, 'idle', [False, False])

enemys = load_enemys('map.txt')

# UI -------------------------------------------------------------------------------------------- #

menu_font_size = int(monitor_size[0]/15)

#get_font(menu_font_size).render('Play', True, (0, 0, 0)).get_width()

DEATH_SCREEN_DURATION = 30
SHOW_SPACE_DURATION = 120
current_death_frame = 0
restart_text = Basic_object([10, screen.get_height()*0.93], get_font(round(screen.get_width()*0.04)).render('Press space to play again', True, (240, 240, 240)))
restart_text.alpha = 0

mode = 'menu'
attack_turn = 'player'
select_enemy = True
enemy_attacking = False
enemy_index = 0
enemy_attacked = None
enemy_animation_reset = False
win = False

# Awful code
buttons = {'menu': {'play': Button((0, 0), None, get_font(menu_font_size), 'Play'),
                    'settings': Button((0, 0), None, get_font(menu_font_size), 'Settings'),
                    'quit': Button((0, 0), None, get_font(menu_font_size), 'Quit'),
                    'back menu': Button((monitor_size[0]*0.06, monitor_size[1]*0.15), None, get_font(menu_font_size), 'Back to menu')}}      
           
images = {'bg menu': pygame.image.load('data/img/backgrounds/bg_menu.png').convert(),
          'bg in game': pygame.image.load('data/img/backgrounds/bg_in_game.png').convert(),
          'title': pygame.image.load('data/img/title.png').convert(),
          'enemy hover': pygame.image.load('data/img/enemy_hover.png').convert(),
          'bg': pygame.image.load('data/img/bg.png').convert(),
          'side borders': pygame.image.load('data/img/borders/side_borders.png').convert(),
          'top border': pygame.image.load('data/img/borders/top_border.png').convert(),
          'bottom border': pygame.image.load('data/img/borders/bottom_border.png').convert(),
          'death screen': pygame.image.load('data/img/death_screen.png').convert(),
          'win screen': pygame.image.load('data/img/win_screen.png').convert()}

images['title'].set_colorkey((255, 255, 255))
images['enemy hover'].set_colorkey((0, 0, 0))
images['side borders'].set_colorkey((255, 255, 255))
images['top border'].set_colorkey((255, 255, 255))
images['bottom border'].set_colorkey((255, 255, 255))

select_enemy_icon = Basic_object([0, 0], images['enemy hover'])
select_enemy_icon.up = True
continue_text = Basic_object([10, screen.get_height()*0.93], get_font(round(screen.get_width()*0.04)).render('Press space to move on to the next stage', True, (240, 240, 240)))
continue_text.alpha = 0

f1_pressed = False
right_down = False
show_menu = False

frame = 0

pygame.mouse.set_visible(False)

# Game loop ------------------------------------------------------------------------------------- #
run = True
while run:
    
    # Event loop -------------------------------------------------------------------------------- #
    clicked = False

    for event in pygame.event.get():
        if event.type == QUIT:
            run = False
            
        if event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                if mode == 'play':
                    pass
                right_down = True
                clicked = True
            if event.button == 3:
                if mode == 'play':
                    pass

        if event.type == MOUSEBUTTONUP:
            if event.button == 1:
                right_down = False

        if event.type == KEYDOWN:       
            if event.key == K_F1:
                f1_pressed = not f1_pressed
                
            if event.key == K_SPACE:
                space_press = True
                if attack_turn == 'stage clear':
                    stage += 1
                    attack_turn = 'player'
                elif mode == 'play again?':
                    initialize_vars()
                elif mode == 'win':
                    initialize_vars()
                    
            if event.key == K_ESCAPE:
                if mode == 'play' and not(attack_turn == 'dying' or attack_turn == 'dead'):
                    show_menu = not show_menu
            
    mx, my = pygame.mouse.get_pos()
    
    # Render ------------------------------------------------------------------------------------ #

    # BUG: Since there are 2 conditions on the game mode, if the first one changes,
    # the second part of it (vector if statement) will render for the changed mode.
    # Meaning half of it would be the start mode in pixel art, and the other half
    # would be the changed mode in vector.

    # Pixel art --------------------------------------------------------------------------------- #
    
    if mode == 'menu':
        canvas.blit(images['bg menu'], (0, 0))
        canvas.blit(images['title'], (150, 80))
        
    elif mode == 'play':
        
        stage_enemys = possible_enemys = [enemy for enemy in enemys if enemy.stage == stage]

        canvas.fill((20, 20, 30))
        pygame.draw.rect(canvas, (50, 50, 70), (0, 280, 640, 80))
       
        for enemy in stage_enemys:
            enemy.render(canvas)
        
        player.render(canvas)
        
        if not show_menu:
            
            for enemy in stage_enemys:
                output = enemy.update()

                if attack_turn == 'enemy':
                    if enemy is enemy_attacked:
                        enemy_animation_reset = output[0]
                        
                    # output[1] is True when the a Creature has completly finished an attack
                    if output[1]:
                        enemy_index += 1
                        start_attack = True
                        if enemy_index >= len(stage_enemys):
                            attack_turn = 'player'
                        enemy_attacking = False
                
            player_animation_reset, finish_attack = player.update()
            
            if enemy_attacked:
                if not(enemy_attacked.alive) and enemy_animation_reset:
                    # Enemy dead
                    enemys.remove(enemy_attacked)
                    stage_enemys.remove(enemy_attacked)
                    enemy_attacked = None
                    enemy_animation_reset = False
            
            if finish_attack:
                attack_turn = 'enemy'
                enemy_index = 0
                start_attack = True

            if stage_enemys == []:
                if last_stage == stage:
                    render_end_screen(loose=False)
                    win = True
                else:
                    attack_turn = 'stage clear'
                        
            if attack_turn == 'player':
                
                enemy_selected = False
                for enemy in stage_enemys:
                    if enemy.rect.collidepoint(mx/RESIZE_SCALE, my/RESIZE_SCALE):
                        enemy_selected = True
                        
                        if select_enemy_icon.up:
                            select_enemy_icon.offset[1] -= 0.5
                            if select_enemy_icon.offset[1] <= -8:
                                select_enemy_icon.up = False
                        else:
                            select_enemy_icon.offset[1] += 0.5
                            if select_enemy_icon.offset[1] >= 0:
                                select_enemy_icon.up = True
                                                        
                        select_enemy_icon.pos = [enemy.health_bar.pos[0] + enemy.health_bar.size[0]/2 - images['enemy hover'].get_width()/2, enemy.health_bar.pos[1] - 12]
                        select_enemy_icon.render(canvas)

                        if clicked:
                            player.attack(enemy)
                            attack_turn = 'player mid attack'
                            enemy_attacked = enemy

                if not enemy_selected:
                    select_enemy_icon.offset[1] = 0

            elif attack_turn == 'enemy':
                if enemy_index >= len(stage_enemys):
                    attack_turn = 'player'
                else:
                    if start_attack and stage_enemys[enemy_index].alive:
                        stage_enemys[enemy_index].attack(player)
                        start_attack = False
                        enemy_attacking = True

            elif attack_turn == 'dying':
                if player_animation_reset:
                    attack_turn = 'dead'

            elif attack_turn == 'dead':
                render_end_screen()

        if not player.alive:
            if not attack_turn == 'dead':
                attack_turn = 'dying'

            
        canvas.blit(images['side borders'], (0, 0))
            
        if enemy_attacking:
            borders_y_desired = 12
        elif attack_turn == 'player mid attack':
            borders_y_desired = 20
        else:
            borders_y_desired = 0
            
        if not(attack_turn == 'dead' or win):
            print(frame)
            show_borders(borders_y_desired)

    elif mode == 'play again?' or mode == 'win':
        
        if current_death_frame < DEATH_SCREEN_DURATION or current_death_frame < SHOW_SPACE_DURATION:
            current_death_frame += 1
        if (current_death_frame/SHOW_SPACE_DURATION) * 255 > 0:
            restart_text.img.set_alpha(restart_text.alpha)
        
        restart_text.alpha = (current_death_frame/SHOW_SPACE_DURATION) * 255
        # Alpha value is bigger then 255
        if mode == 'play again?':
            img = images['death screen']
        elif mode == 'win':
            img = images['win screen']
            
        img.set_alpha((current_death_frame/DEATH_SCREEN_DURATION) * 255)
        canvas.blit(img, (0, 0))
        

    screen.blit(pygame.transform.scale(canvas, monitor_size), (0, 0))
    
    # Vector ------------------------------------------------------------------------------------ #
    if mode == 'menu':
        update_menu_buttons(mode)
       
    elif mode == 'play':        
        if show_menu:
            bar = pygame.Surface((int(monitor_size[0]/2.5), monitor_size[1]), SRCALPHA, 32)
            bar.fill((0, 0, 0))
            bar.set_alpha(150)
            screen.blit(bar, (0, 0))
            update_menu_buttons(mode)
        else:
            for key in buttons['menu']:
                buttons['menu'][key].reset()

            if attack_turn == 'stage clear':
                continue_text.alpha += 8
                if continue_text.alpha > 255:
                    continue_text.alpha = 255
            else:
                continue_text.alpha -= 8
                if continue_text.alpha < 0:
                    continue_text.alpha = 0
                    
        if continue_text.alpha > 0:
            continue_text.img.set_alpha(continue_text.alpha)
            continue_text.render(screen)

    elif mode == 'play again?' or mode == 'win':
        if (current_death_frame/SHOW_SPACE_DURATION) * 255 > 0:
            restart_text.render(screen)
    
    if f1_pressed:
        screen.blit(get_font(int(monitor_size[0]*0.02)).render(str(round(clock.get_fps(), 2)) + ' FPS', True, (50, 200, 255)), (0, 0))
    update_cursor()

    # Other ------------------------------------------------------------------------------------- #
    
    # Update ------------------------------------------------------------------------------------ #
    pygame.display.update()
    clock.tick(FPS)
    frame += 1
    
pygame.quit()
sys.exit()
