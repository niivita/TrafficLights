import pygame
import sys

# Constants
WIDTH, HEIGHT = 800, 600
BACKGROUND_COLOR = (255, 255, 255)
CAR_COLOR = (0, 0, 0)
PEDESTRIAN_COLOR = (255, 0, 0)
ROAD_COLOR = (100, 100, 100)
CAR_SPEED = 3
PEDESTRIAN_SPEED = 2

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Intersection Simulation")

# Car class
class Car:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.x += CAR_SPEED

# Pedestrian class
class Pedestrian:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        self.y += PEDESTRIAN_SPEED

# Create cars and pedestrians
cars = [Car(0, 250), Car(0, 350)]
pedestrians = [Pedestrian(400, 0), Pedestrian(500, 0)]

clock = pygame.time.Clock()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    for car in cars:
        car.move()
        if car.x > WIDTH:
            car.x = 0

    for pedestrian in pedestrians:
        pedestrian.move()
        if pedestrian.y > HEIGHT:
            pedestrian.y = 0

    # Drawing the intersection
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, ROAD_COLOR, (0, 200, WIDTH, 200))
    for car in cars:
        pygame.draw.rect(screen, CAR_COLOR, (car.x, car.y, 40, 20))
    for pedestrian in pedestrians:
        pygame.draw.rect(screen, PEDESTRIAN_COLOR, (pedestrian.x, pedestrian.y, 20, 40))

    pygame.display.flip()
    clock.tick(60)