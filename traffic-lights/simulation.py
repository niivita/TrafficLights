import sys
import pygame
import time


# the four lights
trafficLights = {}
# coordinates for lights
lightCords = {"north": (220, 170), "east": (220, 440), "south": (440, 440), "west": (440, 170)}

# images for each light signal
redSignal = pygame.image.load("signals/red.png")
yellowSignal = pygame.image.load("signals/yellow.png")
greenSignal = pygame.image.load("signals/green.png")
turnSignal = pygame.image.load("signals/turn.png")

# Coordinates of vehicles' start driving __ bound in a given lane
vehicleCoordinates = {"north": {"x": 383, "y": 700}, "northwest": {"x": 365, "y": 700},
                      "east": {"x": 0, "y": 282}, "northeast": {"x": 0, "y": 365},
                      "south": {"x": 295, "y": 0}, "southeast": {"x": 334, "y": 0},
                      "west": {"x": 700, "y": 389}, "southwest": {"x": 700, "y": 344}}

# Coordinates of stop lines for cars driving in _ direction
stopLines = {"north": 460, "east": 240, "south": 240, "west": 460}
# default stops for each direction (add padding to stop line)
defaultStopLine = {"north": 470, "east": 230, "south": 230, "west": 470}

# map to represent the vehicles and their direction TODO: and lane?
vehicles = {"north": {"numCrossed": 0, "lane": []}, "northwest": {"numCrossed": 0, "lane": []},
            "east": {"numCrossed": 0, "lane": []}, "northeast": {"numCrossed": 0, "lane": []},
            "south": {"numCrossed": 0, "lane": []}, "southeast": {"numCrossed": 0, "lane": []},
            "west": {"numCrossed": 0, "lane": []}, "southwest": {"numCrossed": 0, "lane": []}}

# Gap between vehicles
vehicularGap = 20

# create the window, set size
pygame.init()
objects = pygame.sprite.Group()
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
        self.color = color
        if color == "RED":
            screen.blit(redSignal, lightCords[self.key])

        elif color == "YELLOW":
            screen.blit(yellowSignal, lightCords[self.key])

        elif color == "GREEN":
            screen.blit(greenSignal, lightCords[self.key])

        elif color == "TURN":
            screen.blit(turnSignal, lightCords[self.key])

# a single vehicle
class Vehicle(pygame.sprite.Sprite):
    def __init__(self, orientation, direction):
        pygame.sprite.Sprite.__init__(self)
        # car orientation [NSEW]
        self.orientation = orientation
        # car direction [is it turning?]
        self.direction = direction
        # speed for this car (TODO: may be a list of multiple types)
        self.speed = 5 # TODO: Speed Struct
        # the coordinates for this car based on its direction
        self.location = vehicleCoordinates[direction]
        # image for this vehicle TODO: will need to be dynamic and have rotated vehicles for each orientation
        path = orientation+"Bus.png"
        self.image = pygame.image.load(path)
        # ( path = "images/" + direction + "/" + vehicleClass + ".png)
        vehicles[direction]["lane"].append(self)
        # car number in the list
        self.index = len(vehicles[direction]["lane"]) - 1
        # indicate if it has crossed the stop line TODO: maybe a boolean? (taken from other)
        self.crossed = 0

        # determine its stopping distance
        # if there are more vehicles in the lane, and has not passed the stop line
        if len(vehicles[direction]["lane"]) > 1 and vehicles[direction]["numCrossed"] == 0:
            # TODO: all cars same length? (if so can simplify)
            match orientation:
                case "north":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - vehicles[direction]["lane"][self.index - 1].image.get_rect().height - vehicularGap
                case "south":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - vehicles[direction]["lane"][self.index - 1].image.get_rect().height - vehicularGap
                case "east":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - vehicles[direction]["lane"][self.index - 1].image.get_rect().width - vehicularGap
                case "west":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - vehicles[direction]["lane"][self.index - 1].image.get_rect().width - vehicularGap
        # no cars in lane, just stop at given
        else:
            self.stop_dist = defaultStopLine[orientation]

        # Set new starting and stopping coordinate
        match orientation:
            case "north":
                self.location["y"] += self.image.get_rect().height + vehicularGap
            case "south":
                self.location["y"] -= self.image.get_rect().height + vehicularGap
            case "east":
                self.location["y"] += self.image.get_rect().width + vehicularGap
            case "west":
                self.location["y"] -= self.image.get_rect().width + vehicularGap

        objects.add(self)

    def render(self, screen):
        screen.blit(self.image, (self.location["x"], self.location["y"]))

    def move(self):
        match self.direction:
            case "south":
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] + self.image.get_rect().height >= stopLines[self.orientation]:
                    self.crossed = 1

                # if the car hasn't reached the stop yet, has already crossed, or the light is green/yellow
                # AND it's the first car, or there is enough space behind the next vehicle => Move Car
                if (self.location["y"]+self.image.get_rect().height <= self.stop_dist or self.crossed == 1 or (trafficLights[self.orientation].color == "GREEN" or trafficLights[self.orientation].color == "YELLOW")) \
                    and (self.index == 0 or self.location["y"] + self.image.get_rect().height > (vehicles[self.direction]["lane"][self.index-1].location["y"] - vehicularGap)):
                    self.location["y"] += self.speed
            case "north":
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] + self.image.get_rect().height <= stopLines[self.orientation]:
                    self.crossed = 1

                # if the car hasn't reached the stop yet, has already crossed, or the light is green/yellow
                # AND it's the first car, or there is enough space behind the next vehicle => Move Car
                if (self.location["y"] >= self.stop_dist or self.crossed == 1 or (trafficLights[self.orientation].color == "GREEN" or trafficLights[self.orientation].color == "YELLOW")) \
                    and (self.index == 0 or self.location["y"] + self.image.get_rect().height < (vehicles[self.direction]["lane"][self.index - 1].location["y"] - vehicularGap)):
                    self.location["y"] -= self.speed

            case "west":
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] + self.image.get_rect().width <= stopLines[self.orientation]:
                    self.crossed = 1
                # if the car hasn't reached the stop yet, has already crossed, or the light is green/yellow
                # AND it's the first car, or there is enough space behind the next vehicle => Move Car
                if (self.location["x"] >= self.stop_dist or self.crossed == 1 or (trafficLights[self.orientation].color == "GREEN" or trafficLights[self.orientation].color == "YELLOW")) \
                    and (self.index == 0 or self.location["x"] + self.image.get_rect().width < (vehicles[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap)):
                    self.location["x"] -= self.speed
            case "east":
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] + self.image.get_rect().width >= stopLines[self.orientation]:
                    self.crossed = 1
                # if the car hasn't reached the stop yet, has already crossed, or the light is green/yellow
                # AND it's the first car, or there is enough space behind the next vehicle => Move Car
                if (self.location["x"]+self.image.get_rect().height <= self.stop_dist or self.crossed == 1 or (trafficLights[self.orientation].color == "GREEN" or trafficLights[self.orientation].color == "YELLOW")) \
                    and (self.index == 0 or self.location["x"] + self.image.get_rect().width > (vehicles[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap)):
                    self.location["x"] += self.speed


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

        # display the vehicles
        for vehicle in objects:
            screen.blit(vehicle.image, [vehicle.location["x"], vehicle.location["y"]])
            vehicle.move()

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

    # create vehicle (TODO: one for now .. future a method)
    Vehicle("north", "north")
    Vehicle("south", "south")
    Vehicle("east", "east")
    Vehicle("west", "west")

    # track light timing
    t = 0

    # keep lights and vehicles going forever
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        # redraw background (over old cars)
        screen.blit(background, (0, 0))

        # traffic timer logic
        #  floating point math
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
            t = -0.1

        # re-render lights (over new bg)
        trafficLights["north"].set_color(trafficLights["north"].color)
        trafficLights["south"].set_color(trafficLights["south"].color)
        trafficLights["east"].set_color(trafficLights["east"].color)
        trafficLights["west"].set_color(trafficLights["west"].color)

        # re-render vehicles at new location (after moving)
        for vehicle in objects:
            screen.blit(vehicle.image, [vehicle.location["x"], vehicle.location["y"]])
            vehicle.move()

        # update display
        pygame.display.update()

        # increment timer for lights
        t += .1
        time.sleep(.1)  # stops script for .1 seconds (for animation)


Main()


