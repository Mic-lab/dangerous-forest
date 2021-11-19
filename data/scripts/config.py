import pygame
from os.path import dirname

print(__cached__)
data_path = __file__.replace('\\', '/')
data_path = data_path.split('/')[:-2]
data_path = '/'.join(data_path)

pygame.mixer.init()

print(__file__)
print(f'{data_path}/audio/select.wav')

sounds = {'select': pygame.mixer.Sound(f'{data_path}/audio/select.wav'),
          'click': pygame.mixer.Sound(f'{data_path}/audio/click.wav'),
          'hit': pygame.mixer.Sound(f'{data_path}/audio/hit.wav')}

sounds['hit'].set_volume(0.1)

def load_spritesheet(
        actions, sprite_sheet_path,
        size, colorkey, duration, scale=1):
    size[0] *= scale
    size[1] *= scale
    
    animation_data = {}
    for i, path in enumerate(sprite_sheet_path):
        og_img = pygame.image.load(path)
        sprite_sheet = pygame.transform.scale(
            og_img, (og_img.get_width()*scale,
                     og_img.get_height()*scale)
            )
        animation_data[actions[i]] = []
        for col in range(int(sprite_sheet.get_width()/size[0])):    
            img = pygame.Surface(size)
            img.blit(sprite_sheet, (0, 0),
                     (size[0] * col, 0, size[0], size[1]))
            img = img.convert()
            if not(colorkey is None):
                img.set_colorkey(colorkey)
            animation_data[actions[i]].append([duration[i][col], img])

    return animation_data
    
def load_player(actions, durations, scale, path=f'{data_path}/img/player/Adventurer/Individual Sprites/'):
    animation_data = {}
    
    for i, action in enumerate(actions):
        animation_data[action] = []
        for j, duration in enumerate(durations[i]):
            img = pygame.image.load(
                f'{path}adventurer-{action}-0{j}.png').convert()
            img.set_colorkey((0, 0, 0))
            img = pygame.transform.scale(img, (img.get_width()*scale,
                                               img.get_height()*scale))
            animation_data[action].append([duration, img])
                
    return animation_data

def transparent_filter(surf, color, colorkey, alpha):
    surf = surf.copy()
    surf_copy = surf.copy()
    surf_copy.set_colorkey(colorkey)
    surf_copy = pygame.mask.from_surface(surf_copy)
    surf_copy = surf_copy.to_surface()
    surf_copy.set_colorkey((255, 255, 255))
    bg = surf.copy()
    bg.fill(color)
    bg.blit(surf_copy, (0, 0))
    bg.set_colorkey((0, 0, 0))
    bg.set_alpha(alpha)
    surf.blit(bg, (0, 0))
    return surf

def get_center_pos(surf1, surf2):
    x = surf1.get_width()/2 - surf2.get_width()/2
    y = surf1.get_height()/2 - surf2.get_height()/2
    return [x, y]

