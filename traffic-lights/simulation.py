import pygame
import threading
import time


# the four lights
trafficLights = {}
# coordinates for lights
lightCords = {"north": (220, 170), "east": (220, 440), "south": (440, 440), "west": (440, 170)}

redSignal = pygame.image.load('signals/red.png')
yellowSignal = pygame.image.load('signals/yellow.png')
greenSignal = pygame.image.load('signals/green.png')
turnSignal = pygame.image.load('signals/turn.png')

# create the window, set size
pygame.init()
simulation = pygame.sprite.Group()
screenSize = (700, 700)
screen = pygame.display.set_mode(screenSize)


# a single traffic light
class TrafficLight:
    def __init__(self, color, key):
        self.redLight = "RED"
        self.yellowLight = "YELLOW"
        self.greenLight = "GREEN"
        self.turnLight = "TURN"
        self.color = color
        self.key = key
        self.set_color(color)

    # sets the color of the diagram
    def set_color(self, color):
        if color == "RED":
            screen.blit(redSignal, lightCords[self.key])

        elif color == "YELLOW":
            screen.blit(yellowSignal, lightCords[self.key])

        elif color == "GREEN":
            screen.blit(greenSignal, lightCords[self.key])

        elif color == "TURN":
            screen.blit(turnSignal, lightCords[self.key])


# instantiates traffic lights
def create_traffic_lights():
    trafficLights["north"] = TrafficLight("RED", "north")
    trafficLights["south"] = TrafficLight("RED", "south")
    trafficLights["east"] = TrafficLight("GREEN", "east")
    trafficLights["west"] = TrafficLight("GREEN", "west")
    # update display after setting
    pygame.display.update()


# TODO: possibly involve car-movement methods in here? (a thread workaround)
# times each light
def traffic_timer():
    t = 0
    while t <= 34:
        t = round(t, 1)

        # @ 9s, change E/W light to Yellow {9s Green}
        if t == 9:
            trafficLights["east"].set_color("YELLOW")
            trafficLights["west"].set_color("YELLOW")

        # @ 12s, change E/W light to Turn {3s Yellow}
        if t == 12:
            trafficLights["east"].set_color("TURN")
            trafficLights["west"].set_color("TURN")

        # @ 16s, change E/W light to Red {4s Turn}
        if t == 16:
            trafficLights["east"].set_color("RED")
            trafficLights["west"].set_color("RED")

        # delay & @ 17s, change N/S light to Green {17s red}
        if t == 17:
            trafficLights["north"].set_color("GREEN")
            trafficLights["south"].set_color("GREEN")

        # @ 21s, change N/S light to Yellow {9s Green}
        if t == 26:
            trafficLights["north"].set_color("YELLOW")
            trafficLights["south"].set_color("YELLOW")

        # @ 29s, change N/S light to Turn {3s Yellow}
        if t == 29:
            trafficLights["north"].set_color("TURN")
            trafficLights["south"].set_color("TURN")

        # @ 33, change N/S light to Turn {4s Turn}
        if t == 33:
            trafficLights["north"].set_color("RED")
            trafficLights["south"].set_color("RED")

        # @ 34s, change E/W light to Green {17s Red}
        if t == 37:
            trafficLights["east"].set_color("GREEN")
            trafficLights["west"].set_color("GREEN")

        # update display
        pygame.display.update()
        t += .1
        time.sleep(.1)  # stops script for .1 seconds (for animation)


class Main:
    # set background first (bottom - most layer)
    background = pygame.image.load('bg_intersection.png')
    screen.blit(background, (0, 0))
    # create lights
    create_traffic_lights()

    # thread1 = threading.Thread(name="initialization", target=createTrafficLights, args=())  # initialization
    # thread1.daemon = True
    # thread1.start()

    # thread2 = threading.Thread(name="generateVehicles", target=generateVehicles, args=())  # Generating vehicles
    # thread2.daemon = True
    # thread2.start()

    # keep lights and vehicles going forever (concurrency issue) [combine into one method?]
    while True:
        traffic_timer()


Main()


