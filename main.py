import pygame
import settings


screen = pygame.display.set_mode((settings.WIDTH, settings.HIGHT))
pygame.display.set_caption(settings.CAPTION)


class UserInput:
    def __init__(self):
        self.inputs = []

    def get_input(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self.inputs.append(mouse_pos)
        if len(self.inputs) == 2:
            inputs = self.inputs.copy()
            self.inputs.clear()
            return inputs
        return None


run = True
import time
clock = pygame.time.Clock()
userinput = UserInput()
while run:
    clock.tick(60)
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False

    coordinates = userinput.get_input(events)
    if coordinates:
        print(coordinates)


stack = [1, 2, 3]
print(f"stack in main.py: {stack}")
