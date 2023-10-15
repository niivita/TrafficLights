import time
import tkinter as tk
# import pygame

# Single light
class TrafficLight:

    def __init__(self, color, offset):
        self.offset = offset  # position left to right for this instance to draw its light
        self.canvas = canvas
        canvas.create_rectangle(offset + 0, 30, offset + 100, 370, fill="black")
        canvas.create_oval(offset + 3, 40, offset + 100, 140, fill="grey")
        canvas.create_oval(offset + 3, 150, offset + 100, 250, fill="grey")
        canvas.create_oval(offset + 3, 260, offset + 100, 360, fill="grey")
        self.redLight = canvas.create_oval(self.offset + 3, 40, self.offset + 100, 140, fill="grey")
        self.yellowLight = canvas.create_oval(self.offset + 3, 150, self.offset + 100, 250, fill="grey")
        self.greenLight = canvas.create_oval(self.offset + 3, 260, self.offset + 100, 360, fill="grey")

        self.setColor(color)

    # sets the color
    def setColor(self, color):
        if color == "RED":
            canvas.itemconfig(self.redLight, fill="red")
            canvas.itemconfig(self.yellowLight, fill="grey")
            canvas.itemconfig(self.greenLight, fill="grey")
        elif color == "YELLOW":
            canvas.itemconfig(self.redLight, fill="grey")
            canvas.itemconfig(self.yellowLight, fill="yellow")
            canvas.itemconfig(self.greenLight, fill="grey")
        elif color == "GREEN":
            canvas.itemconfig(self.redLight, fill="grey")
            canvas.itemconfig(self.yellowLight, fill="grey")
            canvas.itemconfig(self.greenLight, fill="green")

# Pedestrian light
class PedestrianLight:

    def __init__(self, offset):
        self.offset = offset
        self.canvas = canvas
        self.blueLight = canvas.create_oval(self.offset + 40, 370, self.offset + 60, 390, fill="grey")
        self.activated = False

    # Turn on the pedestrian light (make it blue)
    def activate(self):
        canvas.itemconfig(self.blueLight, fill="blue")
        self.activated = True

    # Turn off the pedestrian light
    def deactivate(self):
        canvas.itemconfig(self.blueLight, fill="grey")
        self.activated = False

    # Check if the pedestrian light is activated
    def is_activated(self):
        return self.activated

# create GUI
root = tk.Tk()
root.title("Traffic Light Simulation")
canvas = tk.Canvas(root, width=450, height=400, bg="white")
canvas.pack()

# pygame.init()
# simulation = pygame.sprite.Group()

# lights within logic
trafficLights = [TrafficLight("RED", 0), TrafficLight("GREEN", 110), TrafficLight("RED", 220),
                 TrafficLight("GREEN", 330)]
pedestrianLights = [PedestrianLight(0), PedestrianLight(110), PedestrianLight(220), PedestrianLight(330)]



# update the light GUIs
def update_traffic_lights():
    root.update()

# Loop to change light colors based on time
# { Green(s) + Yellow(s) = Red(s) }
t = 0
while t <= 12: #24
    t = round(t, 1)

    # @ 9s, change E/W light to Yellow {9s Green}
    if t == 4: #9
        trafficLights[1].setColor("YELLOW")
        trafficLights[3].setColor("YELLOW")
        pedestrianLights[1].activate()
        pedestrianLights[3].activate()
        pedestrianLights[0].activate()
        pedestrianLights[2].activate()

    # @ 11s, change E/W light to Red {2s Yellow}
    if t == 5: #11
        trafficLights[1].setColor("RED")
        trafficLights[3].setColor("RED")
        pedestrianLights[0].activate()
        pedestrianLights[2].activate()
        pedestrianLights[1].deactivate()
        pedestrianLights[3].deactivate()

    # delay & @ 11s, change N/S light to Green {13s red}
    if t == 6: #12
        trafficLights[0].setColor("GREEN")
        trafficLights[2].setColor("GREEN")
        pedestrianLights[0].activate()
        pedestrianLights[2].activate()
        pedestrianLights[1].deactivate()
        pedestrianLights[3].deactivate()

    # @ 21s, change N/S light to Yellow {9s Green}
    if t == 10: #21
        trafficLights[0].setColor("YELLOW")
        trafficLights[2].setColor("YELLOW")
        pedestrianLights[0].activate()
        pedestrianLights[2].activate()
        pedestrianLights[1].deactivate()
        pedestrianLights[3].deactivate()

    # @ 23s, change N/S light to Red {2s Yellow}
    if t == 11: #23
        trafficLights[0].setColor("RED")
        trafficLights[2].setColor("RED")
        pedestrianLights[1].activate()
        pedestrianLights[3].activate()

    # @ 24s, change E/W light to Green {13s Red}
    if t == 12: #24
        trafficLights[1].setColor("GREEN")
        trafficLights[3].setColor("GREEN")
        pedestrianLights[1].activate()
        pedestrianLights[3].activate()
        pedestrianLights[0].deactivate()
        pedestrianLights[2].deactivate()

    # update GUI with new colors
    update_traffic_lights()
    t += .1
    time.sleep(.1)  # stops script for .1 seconds (for animation)




root.mainloop()
