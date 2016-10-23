import sys
import pygame
from chip8 import Chip8

chip = Chip8()

chip.initialize_vm()

program = bytearray(open("test", "rb").read())

chip.load_game(program)

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


while running:
    screen.blit(get_surface_from_chip_screen(), (0,0))
    pygame.display.flip()
    chip.emulate_cycle()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            sys.exit()