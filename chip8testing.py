import sys
import pygame
from chip8 import Chip8

chip = Chip8()

chip.initialize_vm()

program = bytearray(open("BLINKY", "rb").read())

chip.load_game(program)

keys = {
    pygame.K_1: 0x1, pygame.K_2: 0x2, pygame.K_3: 0x3, pygame.K_4: 0xC,
    pygame.K_q: 0x4, pygame.K_w: 0x5, pygame.K_e: 0x6, pygame.K_r: 0xD,
    pygame.K_a: 0x7, pygame.K_s: 0x8, pygame.K_d: 0x9, pygame.K_f: 0xE,
    pygame.K_z: 0xA, pygame.K_x: 0x0, pygame.K_c: 0xB, pygame.K_v: 0xF
}

screen = pygame.display.set_mode((64*10, 32*10))
pygame.display.flip()
running = True

def get_surface_from_chip_screen():
    surface = pygame.Surface((64, 32))
    for index, value in enumerate(chip.screen):
        if value:
            x = int(index % 64)
            y = int(index / 64)
            surface.set_at((x,y), pygame.Color("White"))
    return pygame.transform.scale(surface, (64*10, 32*10)).convert()


clock = pygame.time.Clock()

while running:
    screen.blit(get_surface_from_chip_screen(), (0,0))
    pygame.display.flip()
    chip.emulate_cycle()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()
        # VM KEY
        if event.type == pygame.KEYDOWN:
            if keys.has_key(event.key):
                chip.press_key(keys[event.key])
        elif event.type == pygame.KEYUP:
            if keys.has_key(event.key):
                chip.release_key(keys[event.key])
    chip.emulate_clocks(clock.tick(2042))
