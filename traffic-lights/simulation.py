import random
import sys
import threading

import pygame
import time

# all possible directions {orientation : [directions]}
directions = {"north": ["northwest", "north", "northRighteast"],
              "south": ["southeast", "south", "southRightwest"],
              "west": ["southwest", "west", "westRightnorth"],
              "east": ["northeast", "east", "eastRightsouth"]}

p_directions = {"north": ["northLeft", "northRight"],
                "south": ["southLeft", "southRight"],
                "west": ["westTop", "westBottom"],
                "east": ["eastTop", "eastBottom"]}

# the four lights
trafficLights = {}
# coordinates for lights
lightCords = {"north": (220, 170), "east": (220, 440), "south": (440, 440), "west": (440, 170)}

# images for each light signal
redSignal = pygame.image.load("visuals/signals/red.png")
yellowSignal = pygame.image.load("visuals/signals/yellow.png")
greenSignal = pygame.image.load("visuals/signals/green.png")
turnSignal = pygame.image.load("visuals/signals/turn.png")

# Coordinates of pedestrian spawn
pedestrianCoordinates = {"northLeft": {"x": 270, "y": 700}, "southLeft": {"x": 270, "y": 0},
                         "northRight": {"x": 420, "y": 700}, "southRight": {"x": 420, "y": 0},
                         "eastTop": {"x": 0, "y": 270}, "westTop": {"x": 700, "y": 270},
                         "eastBottom": {"x": 0, "y": 415}, "westBottom": {"x": 700, "y": 415}}

# Coordinates of vehicles' start driving __ bound in a given lane
vehicleCoordinates = {"north": {"x": 383, "y": 700}, "northwest": {"x": 356, "y": 700}, "northRighteast": {"x": 383, "y": 700},
                      "east": {"x": -300, "y": 282}, "northeast": {"x": -300, "y": 252}, "eastRightsouth": {"x": -300, "y": 282}, 
                      "south": {"x": 295, "y": 0}, "southeast": {"x": 325, "y": 0}, "southRightwest": {"x": -300, "y": 282}, 
                      "west": {"x": 800, "y": 389}, "southwest": {"x": 800, "y": 419}, "westRightnorth": {"x": -300, "y": 282}}

# Coordinates of stop lines for cars driving in _ direction
stopLines = {"north": 460, "east": 240, "south": 240, "west": 460}
# Coordinates for cub lines for pedestrians walking in _ direction
curbLines = {"north": 430, "east": 270, "south": 270, "west": 430}

# map to represent the vehicles and their direction
vehicles = {"north": {"numCrossed": 0, "lane": []}, "northwest": {"numCrossed": 0, "lane": []},
            "east": {"numCrossed": 0, "lane": []}, "northeast": {"numCrossed": 0, "lane": []},
            "south": {"numCrossed": 0, "lane": []}, "southeast": {"numCrossed": 0, "lane": []},
            "west": {"numCrossed": 0, "lane": []}, "southwest": {"numCrossed": 0, "lane": []},
            "northRighteast": {"numCrossed": 0, "lane": []}, "eastRightsouth": {"numCrossed": 0, "lane": []},
            "southRightwest": {"numCrossed": 0, "lane": []}, "westRightnorth": {"numCrossed": 0, "lane": []}}

# map to represent pedestrians and their direction
pedestrians = {"northLeft": {"numCrossed": 0, "lane": []}, "northRight": {"numCrossed": 0, "lane": []},
               "eastTop": {"numCrossed": 0, "lane": []}, "southRight": {"numCrossed": 0, "lane": []},
               "southLeft": {"numCrossed": 0, "lane": []}, "eastBottom": {"numCrossed": 0, "lane": []},
               "westTop": {"numCrossed": 0, "lane": []}, "westBottom": {"numCrossed": 0, "lane": []}}

# Gap between vehicles
vehicularGap = 20
# Gap between pedestrians (social distancing)
pedestrianGap = 20
# size of pedestrian
pedestrianSize = 23

# create the window, set size
pygame.init()
objects = pygame.sprite.Group()
screenSize = (700, 700)
screen = pygame.display.set_mode(screenSize)

# crosswalk occupied checks by pedestrians
northXwalk = 0
southXwalk = 0
eastXwalk = 0
westXwalk = 0

# crosswalk occupied checks by cars
northDrive = 0
southDrive = 0
westDrive = 0
eastDrive = 0

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
        # speed for this car
        self.speed = 5
        # the coordinates for this car based on its direction
        self.location = vehicleCoordinates[direction].copy()
        # image for this vehicle
        path = "visuals/vehicles/" + orientation + "Car.png"
        self.image = pygame.image.load(path)
        # ( path = "images/" + direction + "/" + vehicleClass + ".png)
        # car number in the list
        self.index = len(vehicles[direction]["lane"])
        vehicles[direction]["lane"].append(self)
        # indicate if it has crossed the stop line (0 or 1)
        self.crossed = 0
        # indicate if the car has turned
        self.hasTurned = False

        # determine its stopping distance
        # if there are more vehicles in the lane, and has not passed the stop line
        if len(vehicles[direction]["lane"]) > 1 and self.index > vehicles[direction]["numCrossed"]:
            # TODO: all cars same length? (if so can simplify)
            match orientation:
                case "north":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - \
                                     vehicles[direction]["lane"][self.index - 1].image.get_rect().height + vehicularGap
                case "south":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist + \
                                     vehicles[direction]["lane"][self.index - 1].image.get_rect().height - vehicularGap
                case "east":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist + \
                                     vehicles[direction]["lane"][self.index - 1].image.get_rect().width - vehicularGap
                case "west":
                    self.stop_dist = vehicles[direction]["lane"][self.index - 1].stop_dist - \
                                     vehicles[direction]["lane"][self.index - 1].image.get_rect().width + vehicularGap
        # no cars in lane, just stop at given
        else:
            self.stop_dist = stopLines[orientation]

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

    def move(self):
        global southDrive
        match self.direction:
            case "north":
                # if the light is red for this lane
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["y"] -= self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["y"] > self.stop_dist and self.index == vehicles[self.direction]["numCrossed"]:
                        self.location["y"] = max(self.location["y"] - self.speed, self.stop_dist + 3)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["y"] > (
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] +
                            vehicles[self.direction]["lane"][
                                self.index - 1].image.get_rect().height + vehicularGap) and self.location[
                        "y"] >= self.stop_dist:
                        self.location["y"] -= self.speed
                # otherwise if green / yellow, move
                else:
                    self.location["y"] -= self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] <= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "south":
                # if the light is red for this lane
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["y"] += self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["y"] + self.image.get_rect().height < self.stop_dist and self.index == \
                            vehicles[self.direction]["numCrossed"]:
                        self.location["y"] = min(self.location["y"] + self.speed,
                                                 self.stop_dist - 3 - self.image.get_rect().height)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["y"] + self.image.get_rect().height < (
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] - vehicularGap) and \
                            self.location["y"] + self.image.get_rect().height <= self.stop_dist:
                        self.location["y"] += self.speed
                # otherwise if green / yellow, move
                else:
                    self.location["y"] += self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] + self.image.get_rect().height >= stopLines[
                    self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "east":
                # if the light is red for this lane
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["x"] += self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["x"] + self.image.get_rect().width < self.stop_dist and self.index == \
                            vehicles[self.direction]["numCrossed"]:
                        self.location["x"] = min(self.location["x"] + self.speed,
                                                 self.stop_dist - 3 - self.image.get_rect().width)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["x"] + self.image.get_rect().width < (
                            vehicles[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap) and \
                            self.location["x"] + self.image.get_rect().width <= self.stop_dist:
                        self.location["x"] += self.speed
                # otherwise if green / yellow, move
                else:
                    self.location["x"] += self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] + self.image.get_rect().width >= stopLines[
                    self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "west":
                # if the light is red for this lane
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["x"] -= self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["x"] > self.stop_dist and self.index == vehicles[self.direction]["numCrossed"]:
                        self.location["x"] = max(self.location["x"] - self.speed, self.stop_dist + 3)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["x"] > (vehicles[self.direction]["lane"][self.index - 1].location["x"] +
                                               vehicles[self.direction]["lane"][
                                                   self.index - 1].image.get_rect().width + vehicularGap) \
                            and self.location["x"] >= self.stop_dist:
                        self.location["x"] -= self.speed
                # otherwise if green / yellow, move
                else:
                    self.location["x"] -= self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] <= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

#-----------------------------------------------LEFT TURNS-----------------------------------------------------------
#-----------------------------------------------LEFT TURNS-----------------------------------------------------------
#-----------------------------------------------LEFT TURNS-----------------------------------------------------------
            # northwest
            case "northwest":
                # is already turned, keep moving
                if self.hasTurned:
                    self.location["x"] -= self.speed
                # regardless of light, if car is in intersection, turn
                elif self.crossed == 1:
                    # move until it reaches the second boundary
                    if self.location["y"] > stopLines[self.orientation] - 115:
                        self.location["y"] -= self.speed
                    # when boundary is reached, load new car (prevent overlap of new cars
                    elif self.index == 0 or self.location["x"] > \
                            vehicles[self.direction]["lane"][self.index - 1].location["x"] \
                            + 4 + vehicularGap + self.image.get_rect().height:
                        self.location["y"] -= self.image.get_rect().width
                        path = "visuals/vehicles/eastCar.png"
                        self.image = pygame.image.load(path)
                        self.hasTurned = True
                        self.location["x"] = max(self.location["x"],
                                                 vehicles[self.direction]["lane"][self.index - 1].location[
                                                     "x"] + 4 + vehicularGap)
                        self.location["x"] -= self.speed

                # otherwise, check lights - if the light is essentially red for this lane
                elif trafficLights[self.orientation].color != "TURN":
                    # otherwise, hasn't crossed initial line, follow north logic:
                    # if first car and hasn't reached stop line
                    if self.location["y"] > self.stop_dist and self.index == \
                            vehicles[self.direction]["numCrossed"]:
                        self.location["y"] = max(self.location["y"] - self.speed,
                                                 self.stop_dist + 3)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["y"] > (
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] + vehicularGap + self.image.get_rect().height) and \
                            self.location["y"] >= self.stop_dist:
                        self.location["y"] -= self.speed
                else:
                    self.location["y"] -= self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] <= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "southeast":
                # is already turned, keep moving
                if self.hasTurned:
                    self.location["x"] += self.speed
                # regardless of light, if car is in intersection, turn
                elif self.crossed == 1:
                    # move until it reaches the second boundary
                    if self.location["y"] + self.image.get_rect().height < stopLines[self.orientation] + 115:
                        self.location["y"] += self.speed
                    # when boundary is reached, load new car (prevent overlap of new cars
                    elif self.index == 0 or self.location["x"] + self.image.get_rect().height < \
                            vehicles[self.direction]["lane"][self.index - 1].location["x"] - 4 - vehicularGap:
                        self.location["y"] += self.image.get_rect().height
                        path = "visuals/vehicles/eastCar.png"
                        self.image = pygame.image.load(path)
                        self.hasTurned = True
                        self.location["x"] = min(self.location["x"],
                                                 vehicles[self.direction]["lane"][self.index - 1].location[
                                                     "x"] - 4 - vehicularGap)
                        self.location["x"] += self.speed

                # otherwise, check lights - if the light is essentially red for this lane
                elif trafficLights[self.orientation].color != "TURN":
                    # otherwise, hasn't crossed initial line, follow south logic:
                    # if first car and hasn't reached stop line
                    if self.location["y"] + self.image.get_rect().height < self.stop_dist and self.index == \
                         vehicles[self.direction]["numCrossed"]:
                        self.location["y"] = min(self.location["y"] + self.speed,
                                             self.stop_dist - 3 - self.image.get_rect().height)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["y"] + self.image.get_rect().height < (
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] - vehicularGap) and \
                            self.location["y"] + self.image.get_rect().height <= self.stop_dist:
                        self.location["y"] += self.speed
                else:
                    self.location["y"] += self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 \
                        and self.location["y"] + self.image.get_rect().height >= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "southwest":
                # is already turned, keep moving
                if self.hasTurned:
                    self.location["y"] += self.speed
                # regardless of light, if car is in intersection, turn
                elif self.crossed == 1:
                    # move until it reaches the second boundary
                    if self.location["x"] > stopLines[self.orientation] - 115:
                        self.location["x"] -= self.speed
                    # when boundary is reached, load new car (prevent overlap of new cars
                    elif self.index == 0 or self.location["y"] < \
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] \
                            + 4 + vehicularGap + self.image.get_rect().width:
                        self.location["x"] -= self.image.get_rect().height
                        path = "visuals/vehicles/southCar.png"
                        self.image = pygame.image.load(path)
                        self.hasTurned = True
                        self.location["y"] = min(self.location["y"],
                                                 vehicles[self.direction]["lane"][self.index - 1].location[
                                                     "y"] + 4 + vehicularGap)
                        self.location["y"] += self.speed

                # otherwise, check lights - if the light is essentially red for this lane
                elif trafficLights[self.orientation].color != "TURN":
                    # otherwise, hasn't crossed initial line, follow west logic:
                    # if first car and hasn't reached stop line
                    if self.location["x"] > self.stop_dist and self.index == vehicles[self.direction]["numCrossed"]:
                        self.location["x"] = max(self.location["x"] - self.speed, self.stop_dist + 3)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["x"] > (vehicles[self.direction]["lane"][self.index - 1].location["x"] +
                                               vehicles[self.direction]["lane"][
                                                   self.index - 1].image.get_rect().width + vehicularGap) \
                            and self.location["x"] >= self.stop_dist:
                        self.location["x"] -= self.speed

                else:
                    self.location["x"] -= self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] <= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

            case "northeast":
                # is already turned, keep moving
                if self.hasTurned:
                    self.location["y"] -= self.speed
                # regardless of light, if car is in intersection, turn
                elif self.crossed == 1:
                    # move until it reaches the second boundary
                    if self.location["x"] + self.image.get_rect().width < stopLines[self.orientation] + 115:
                        self.location["x"] += self.speed
                    # when boundary is reached, load new car (prevent overlap of new cars
                    elif self.index == 0 or self.location["y"] > \
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] \
                            + 4 + vehicularGap + self.image.get_rect().width:
                        self.location["x"] += self.image.get_rect().width
                        path = "visuals/vehicles/northCar.png"
                        self.image = pygame.image.load(path)
                        self.hasTurned = True
                        self.location["y"] = min(self.location["y"],
                                                 vehicles[self.direction]["lane"][self.index - 1].location[
                                                     "y"] + 4 + vehicularGap + self.image.get_rect().height)
                        self.location["y"] -= self.speed

                # otherwise, check lights - if the light is essentially red for this lane
                elif trafficLights[self.orientation].color != "TURN":
                    # otherwise, hasn't crossed initial line, follow east logic:
                    # if first car and hasn't reached stop line
                    if self.location["x"] + self.image.get_rect().width < self.stop_dist and self.index == vehicles[self.direction]["numCrossed"]:
                        self.location["x"] = min(self.location["x"] + self.speed, self.stop_dist - 3 - self.image.get_rect().width)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["x"] + self.image.get_rect().width < (vehicles[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap) \
                            and self.location["x"] + self.image.get_rect().width <= self.stop_dist:
                        self.location["x"] += self.speed

                else:
                    self.location["x"] += self.speed

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] + self.image.get_rect().width >= stopLines[self.orientation]:
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]

#-----------------------------------------------RIGHT TURNS-----------------------------------------------------------
#-----------------------------------------------RIGHT TURNS-----------------------------------------------------------
#-----------------------------------------------RIGHT TURNS-----------------------------------------------------------
            case "eastRightsouth":
                if self.hasTurned:
                    self.location["y"] += self.speed
                # regardless of light, if car is in intersection, turn
                elif self.crossed == 1:
                    # move until it reaches the second boundary
                    if self.location["x"] <= stopLines[self.orientation]- 25:
                        self.location["x"] += self.speed
                    # when boundary is reached, load new car (prevent overlap of new cars
                    elif self.index == 0 or self.location["y"] <= \
                            vehicles[self.direction]["lane"][self.index - 1].location["y"] \
                            + 4 + vehicularGap + self.image.get_rect().height:
                        self.location["x"] += self.image.get_rect().width
                        path = "visuals/vehicles/southCar.png"
                        self.image = pygame.image.load(path)
                        self.hasTurned = True
                        southDrive -= 1
                        self.location["y"] = min(self.location["y"],
                                                 vehicles[self.direction]["lane"][self.index - 1].location[
                                                     "y"] + 4 + vehicularGap)
                        self.location["y"] += self.speed
                # if the light is red for this lane
                elif trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["x"] += self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["x"] + self.image.get_rect().width < self.stop_dist and self.index == \
                            vehicles[self.direction]["numCrossed"]:
                        self.location["x"] = min(self.location["x"] + self.speed,
                                                 self.stop_dist - 3 - self.image.get_rect().width)
                    # otherwise, not first car and distance behind vehicle is large enough
                    elif self.location["x"] + self.image.get_rect().width < (
                            vehicles[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap) and \
                            self.location["x"] + self.image.get_rect().width <= self.stop_dist:
                        self.location["x"] += self.speed
                # otherwise if green / yellow, move
                elif southXwalk == 0:
                    self.location["x"] += self.speed
                    

                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] + self.image.get_rect().width >= stopLines[
                    self.orientation]:
                    southDrive += 1
                    self.crossed = 1
                    vehicles[self.direction]["numCrossed"] += 1
                    # reset the next car's stop ;
                    if self.index + 1 < len(vehicles[self.direction]["lane"]):
                        vehicles[self.direction]["lane"][self.index + 1].stop_dist = stopLines[self.orientation]


class Pedestrian(pygame.sprite.Sprite):
    def __init__(self, orientation, direction):
        pygame.sprite.Sprite.__init__(self)
        # pedestrian orientation [NSEW]
        self.orientation = orientation
        # pedestrian direction [side of street]
        self.direction = direction
        # speed for this pedestrian
        self.speed = 2
        # the coordinates for this car based on its direction
        self.location = pedestrianCoordinates[direction].copy()
        # image for this vehicle
        self.image = pygame.image.load("visuals/pedestrian.png")
        # pedestrian number in the list
        self.index = len(pedestrians[direction]["lane"])
        pedestrians[direction]["lane"].append(self)
        # indicate if it has crossed the stop line (0 or 1)
        self.crossed = 0
        # determine pedestrian stop distance based on size of pedestrian icon
        if len(pedestrians[direction]["lane"]) > 1 and self.index > pedestrians[direction]["numCrossed"]:
            match orientation:
                case "north":
                    self.stop_dist = pedestrians[direction]["lane"][
                                         self.index - 1].stop_dist - pedestrianSize + pedestrianGap
                case "south":
                    self.stop_dist = pedestrians[direction]["lane"][
                                         self.index - 1].stop_dist + pedestrianSize - pedestrianGap
                case "east":
                    self.stop_dist = pedestrians[direction]["lane"][
                                         self.index - 1].stop_dist + pedestrianSize - pedestrianGap
                case "west":
                    self.stop_dist = pedestrians[direction]["lane"][
                                         self.index - 1].stop_dist - pedestrianSize + pedestrianGap
        # no pedestrians in lane, just stop at given
        else:
            self.stop_dist = curbLines[orientation]

            # Set new starting and stopping coordinate
            match orientation:
                case "north":
                    self.location["y"] += pedestrianSize + pedestrianGap
                case "south":
                    self.location["y"] -= pedestrianSize + pedestrianGap
                case "east":
                    self.location["x"] += pedestrianSize + pedestrianGap
                case "west":
                    self.location["x"] -= pedestrianSize + pedestrianGap

            objects.add(self)

    # move pedestrian
    def move(self):
        match self.orientation:
            case "north":
                # if traffic light is red / turn (pedestrian light green)
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["y"] -= self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["y"] > self.stop_dist and self.index == pedestrians[self.direction][
                        "numCrossed"]:
                        self.location["y"] = max(self.location["y"] - self.speed, self.stop_dist + 3)
                    # otherwise, not first person, distance behind vehicle is large enough
                    elif self.location["y"] > (
                            pedestrians[self.direction]["lane"][self.index - 1].location["y"] +
                            pedestrianSize + pedestrianGap) and self.location["y"] >= self.stop_dist:
                        self.location["y"] -= self.speed
                # otherwise if green / yellow, move
                elif (self.direction == "northLeft" and westDrive == 0) or (self.orientation == "northRight" and eastDrive == 0):
                    self.location["y"] -= self.speed
                print(eastDrive)
                if( self.crossed == 1 and (self.location["y"] <= curbLines["south"] + 10)):
                    self.crossed = 0
                    if self.orientation == 'northLeft':
                        westXwalk -= 1
                    else:
                        eastXwalk -= 1
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] <= curbLines[self.orientation]:
                    self.crossed = 1
                    if self.orientation == 'northLeft':
                        westXwalk += 1
                    else:
                        eastXwalk += 1
                    pedestrians[self.direction]["numCrossed"] += 1
                    # reset the next person's stop ;
                    if self.index + 1 < len(pedestrians[self.direction]["lane"]):
                        pedestrians[self.direction]["lane"][self.index + 1].stop_dist = curbLines[self.orientation]

            case "south":
                # if traffic light is red / turn (pedestrian light green)
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if person has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["y"] += self.speed
                    # if first person and hasn't reached stop line
                    elif self.location["y"] + pedestrianSize < self.stop_dist and self.index == \
                            pedestrians[self.direction]["numCrossed"]:
                        self.location["y"] = min(self.location["y"] + self.speed,
                                                 self.stop_dist - 3 - pedestrianSize)
                    # otherwise, not first person,  distance behind person is large enough
                    elif self.location["y"] + pedestrianSize < (
                            pedestrians[self.direction]["lane"][self.index - 1].location["y"] - vehicularGap) and \
                            self.location["y"] + pedestrianSize <= self.stop_dist:
                        self.location["y"] += self.speed
                # otherwise if green / yellow, move
                elif (self.orientation == "southLeft" and westDrive == 0) or (self.orientation == "southRight" and eastDrive == 0):
                    self.location["y"] += self.speed
                if( self.crossed == 1 and (self.location["y"] >= curbLines["north"] - 10)):
                    self.crossed = 0
                    if self.orientation == 'southLeft':
                        westXwalk -= 1
                    else:
                        eastXwalk -= 1
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["y"] >= curbLines[self.orientation]:
                    self.crossed = 1
                    if self.orientation == 'southLeft':
                        westXwalk += 1
                    else:
                        eastXwalk += 1
                    pedestrians[self.direction]["numCrossed"] += 1
                    # reset the next person's stop ;
                    if self.index + 1 < len(pedestrians[self.direction]["lane"]):
                        pedestrians[self.direction]["lane"][self.index + 1].stop_dist = curbLines[self.orientation]

            case "east":
                # if traffic light is red / turn (pedestrian light green)
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if car has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["x"] += self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["x"] + pedestrianSize < self.stop_dist and self.index == \
                            pedestrians[self.direction]["numCrossed"]:
                        self.location["x"] = min(self.location["x"] + self.speed,
                                                 self.stop_dist - 3 - pedestrianSize)
                    # otherwise, not first person, distance behind person is large enough
                    elif self.location["x"] + pedestrianSize < (
                            pedestrians[self.direction]["lane"][self.index - 1].location["x"] - vehicularGap) and \
                            self.location["x"] + pedestrianSize <= self.stop_dist:
                        self.location["x"] += self.speed
                # otherwise if green / yellow, move
                elif (self.orientation == "eastTop" and northDrive == 0) or (self.orientation == "eastBottom" and southDrive == 0):
                    self.location["x"] += self.speed
                if( self.crossed == 1 and (self.location["x"] >= curbLines["west"] - 10)):
                    self.crossed = 0
                    if self.orientation == 'eastTop':
                        northXwalk -= 1
                    else:
                        southXwalk -= 1
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] >= curbLines[self.orientation]:
                    self.crossed = 1
                    if self.orientation == 'eastTop':
                        northXwalk += 1
                    else:
                        southXwalk += 1
                    pedestrians[self.direction]["numCrossed"] += 1
                    # reset the next person's stop ;
                    if self.index + 1 < len(pedestrians[self.direction]["lane"]):
                        pedestrians[self.direction]["lane"][self.index + 1].stop_dist = curbLines[self.orientation]

            case "west":
                # if traffic light is red / turn (pedestrian light green)
                if trafficLights[self.orientation].color == "RED" or trafficLights[self.orientation].color == "TURN":
                    # if person has already crossed, can keep moving
                    if self.crossed == 1:
                        self.location["x"] -= self.speed
                    # if first car and hasn't reached stop line
                    elif self.location["x"] > self.stop_dist and self.index == pedestrians[self.direction][
                        "numCrossed"]:
                        self.location["x"] = max(self.location["x"] - self.speed, self.stop_dist + 3)
                    # otherwise, not first car, distance behind person is large enough
                    elif self.location["x"] > (pedestrians[self.direction]["lane"][self.index - 1].location["x"] +
                                               pedestrianSize + vehicularGap) \
                            and self.location["x"] >= self.stop_dist:
                        self.location["x"] -= self.speed
                elif (self.orientation == "westTop" and northDrive == 0) or (self.orientation == "westBottom" and southDrive == 0):
                    self.location["x"] -= self.speed
                if( self.crossed == 1 and (self.location["y"] <= curbLines["east"] + 10)):
                    self.crossed = 0
                    if self.orientation == 'westTop': 
                        northXwalk -= 1
                    else:
                        southXwalk -= 1
                # if it hasn't already crossed, and has now crossed the stop line boundary
                if self.crossed == 0 and self.location["x"] <= curbLines[self.orientation]:
                    self.crossed = 1
                    if self.orientation == 'westTop':
                        northXwalk += 1
                    else:
                        southXwalk += 1
                    pedestrians[self.direction]["numCrossed"] += 1
                    # reset the next person's stop ;
                    if self.index + 1 < len(pedestrians[self.direction]["lane"]):
                        pedestrians[self.direction]["lane"][self.index + 1].stop_dist = curbLines[self.orientation]


# instantiates traffic lights
def create_traffic_lights():
    trafficLights["north"] = TrafficLight("RED", "north")
    trafficLights["south"] = TrafficLight("RED", "south")
    trafficLights["east"] = TrafficLight("GREEN", "east")
    trafficLights["west"] = TrafficLight("GREEN", "west")
    # update display after setting
    pygame.display.update()


# populate intersection
def populate_intersection():
    while True:
        picker = random.randint(0, 100)
        if picker <= 63:
            create_vehicle()
        else:
            create_pedestrian()
        time.sleep(2)


# instantiate cars randomly
def create_vehicle():
    keys = list(directions.keys())

    # o_num = random.randint(0, 3)
    # d_num = random.randint(0, 1)

    o_num = 3
    d_num = 2

    Vehicle(keys[o_num], directions[keys[o_num]][d_num])


# instantiate pedestrians randomly
def create_pedestrian():
    keys = list(p_directions.keys())

    # o_num = random.randint(0, 3)
    # d_num = random.randint(0, 1)

    # Pedestrian(keys[o_num], p_directions[keys[o_num]][d_num])

    Pedestrian("north", "northRight")


class Simulate:
    # set background first (bottom - most layer)
    background = pygame.image.load('visuals/bg_intersection.png')
    screen.blit(background, (0, 0))

    # create lights
    create_traffic_lights()

    # to continually generate cars and people
    thread = threading.Thread(name="populateIntersection", target=populate_intersection, args=())
    thread.daemon = True
    thread.start()

    # track light timing TODO make 4 way red light longer (time for left over turns)
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

        # @ 12s, change E/W light to Red {3s yellow}
        if t == 12:
            trafficLights["east"].set_color("RED")
            trafficLights["west"].set_color("RED")

        # @ 15s, change E/W light to Turn {3s Red}
        if t == 15:
            trafficLights["east"].set_color("TURN")
            trafficLights["west"].set_color("TURN")

        # @ 19s, change E/W light to Red {4s Turn}
        if t == 19:
            trafficLights["east"].set_color("RED")
            trafficLights["west"].set_color("RED")

        # delay & @ 21s, change N/S light to Green {21s red}
        if t == 21:
            trafficLights["north"].set_color("GREEN")
            trafficLights["south"].set_color("GREEN")

        # @ 30s, change N/S light to Yellow {9s Green}
        if t == 30:
            trafficLights["north"].set_color("YELLOW")
            trafficLights["south"].set_color("YELLOW")

        # @ 33, change N/S light to Red {4s Yellow}
        if t == 33:
            trafficLights["north"].set_color("RED")
            trafficLights["south"].set_color("RED")

        # @ 36s, change N/S light to Turn {3s Red}
        if t == 36:
            trafficLights["north"].set_color("TURN")
            trafficLights["south"].set_color("TURN")

        # @ 40, change N/S light to Turn {4s Turn}
        if t == 40:
            trafficLights["north"].set_color("RED")
            trafficLights["south"].set_color("RED")

        # @ 42s, change E/W light to Green {17s Red}
        if t == 42:
            trafficLights["east"].set_color("GREEN")
            trafficLights["west"].set_color("GREEN")
            t = -0.1

        # re-render lights (over new bg)
        trafficLights["north"].set_color(trafficLights["north"].color)
        trafficLights["south"].set_color(trafficLights["south"].color)
        trafficLights["east"].set_color(trafficLights["east"].color)
        trafficLights["west"].set_color(trafficLights["west"].color)

        # re-render vehicles AND pedestrians at new location (after moving)
        for object in objects:
            screen.blit(object.image, [object.location["x"], object.location["y"]])
            object.move()

        # update display
        pygame.display.update()

        # increment timer for lights
        t += .1
        time.sleep(.05)  # stops script for .1 seconds (for animation)


Simulate()
